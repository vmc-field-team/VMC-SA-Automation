#!/usr/bin/env python

import json
import requests

from time import sleep
from urllib.parse import urlencode

# Created by Chris Lennon VMC SET

def get_token(csp, rtoken):
    params = {'refresh_token': rtoken}
    resp = requests.post(
        '{host}/csp/gateway/am/api/auth/api-tokens/authorize'.format(host=csp), params=params)
    return resp.json()['access_token']


def status_sddc(token, org, name, listAll):
    headers = {'csp-auth-token': token, 'Accept': 'application/json'}
    resp = requests.get(
        'https://vmc.vmware.com/vmc/api/orgs/{orgId}/sddcs'.format(orgId=org), headers=headers)
    orgdata = resp.json()
    if (orgdata):
        if (listAll):
            return(orgdata)
        for sddc in orgdata:
            if sddc['name'] == name:
                return(sddc)
    else:
        return(False)


def sddc_group(token, orgId, delete):
    account =[]
    headers = {'csp-auth-token': token, 'Accept': 'application/json'}
    resp = requests.get(
        'https://vmc.vmware.com/api/inventory/{orgId}/core/deployment-groups?include_deleted_resources=false&trait=AwsVpcAttachmentsTrait'.format(orgId=orgId), headers=headers)
    orgdata = resp.json()
    for org in orgdata['content']:
        print('Group SDDC:', org['name'])
        if delete == True:
            if org['id']:
                print('Deleting group:', org['name'])
                if (org['membership']['included']):
                    #remove sddcs
                    print('Removing SDDC members')
                    for sddc in org['membership']['included']:
                        data = {'type': 'UPDATE_GROUP_MEMBERS',
                                'resource_id': org['id'],
                                'resource_type': 'deployment-group',
                                'config': {'type': 'DeploymentGroupMembersUpdateConfig',
                                        'remove_members': [{
                                            'deployment_id': sddc['deployment_id']
                                        }]
                                    }
                        }     
                        resp = requests.post(
                            'https://vmc.vmware.com/api/inventory/{orgId}/grouping/operations'.format(orgId=orgId), json=data, headers=headers) 
                        sleep(180)
                #get group data
                groupId = org['id']
                resp = requests.get('https://vmc.vmware.com/api/network/{orgId}/core/network-connectivity-configs?group_id={groupId}&include_deleted_resources=false&trait=AwsVpcAttachmentsTrait'.format(
                    orgId=orgId, groupId=groupId), headers=headers)
                groupData = resp.json()
                for group in groupData:
                    print('Removing VPC')
                    resourceId = group['id']                  
                    # remove vpc
                    if group['traits']:
                        if group['traits']['AwsVpcAttachmentsTrait']['accounts']:
                            account = group['traits']['AwsVpcAttachmentsTrait']['accounts'][0]
                            if account['attachments']:
                                account['attachments'][0]['action'] = 'DELETE'
                                if len(account['attachments']) == 2:
                                    account['attachments'][1]['action'] = 'DELETE'
                                data = {'type': 'APPLY_ATTACHMENT_ACTION',
                                        'resource_id': resourceId,
                                        'resource_type': 'network-connectivity-config',
                                        'config': {'type': 'AwsApplyAttachmentActionConfig',
                                                'account': account,
                                                'policy_id': resourceId,
                                                'group_id': groupId}}
                                resp = requests.post(
                                    'https://vmc.vmware.com/api/network/{orgId}/aws/operations'.format(orgId=orgId), json=data, headers=headers)
                                sleep(90)
                            # remove aws account
                            print('Removing AWS account')
                            data = {'type': 'REMOVE_EXTERNAL_ACCOUNT',
                                    'resource_id': resourceId,
                                    'resource_type': 'network-connectivity-config',
                                    'config': {'type': 'AwsRemoveExternalAccountConfig',
                                            'account': account,
                                            'policy_id': resourceId}}
                            resp = requests.post(
                                'https://vmc.vmware.com/api/network/{orgId}/aws/operations'.format(orgId=orgId), json=data, headers=headers)
                            sleep(60)
                    # remove sddc group
                    print('Removing SDDC group')
                    data = {'type': 'DELETE_DEPLOYMENT_GROUP',
                            'resource_id': resourceId,
                            'resource_type': 'network-connectivity-config',
                            'config': {'type': 'AwsDeleteDeploymentGroupConfig',
                                       'policy_id': resourceId,
                                       'group_id': groupId}}
                    resp = requests.post(
                        'https://vmc.vmware.com/api/network/{orgId}/aws/operations'.format(orgId=orgId), json=data, headers=headers)
                    # print(resp)

def remove_sddc(token, org, name):
    headers = {'csp-auth-token': token, 'Accept': 'application/json'}
    params = {'orgID': org}
    resp = requests.get(
        'https://vmc.vmware.com/vmc/api/orgs/{orgId}/sddcs'.format(orgId=org), headers=headers)
    orgdata = resp.json()
    org_list = orgdata
    for orgs in org_list:
        if orgs['name'] == name or name == 'ALL':
            print('Found and removing SDDC: ' +
                  orgs['name'] + ' - ' + orgs['resource_config']['sddc_id'])
            sddcId = orgs['resource_config']['sddc_id']
            resp = requests.delete('https://vmc.vmware.com/vmc/api/orgs/{orgId}/sddcs/{sddcId}'.format(
                orgId=org, sddcId=sddcId), headers=headers)
        # wait_for_task(org, token, json_response['id'], 60)


def create_sddc(token, org, name, cidr, provider, subnetId, region, numHost, networkSegment):
    headers = {'csp-auth-token': token,
               'Content-Type': 'application/json', 'Accept': 'application/json'}
    connectedAccount = get_connected_account(org, token)
    data = {
        'name': name,
        'account_link_sddc_config': [
            {
                'customer_subnet_ids': [
                    subnetId
                ],
                'connected_account_id': connectedAccount
            }
        ],
        'vpc_cidr': cidr,
        'provider': provider.upper(),
        'sso_domain': 'vmc.local',
        'num_hosts': numHost,
        'sddc_type': '1NODE',
        'deployment_type': 'SingleAZ',
        'vxlan_subnet': networkSegment,
        'region': region
    }
    resp = requests.post('https://vmc.vmware.com/vmc/api/orgs/{orgId}/sddcs'.format(
        orgId=org), json=data, headers=headers)
    json_response = resp.json()
    print(name + ' SDDC ' + str(json_response['status']))
    if json_response['status'] not in (400, 500):
        return json_response['id']
    else:
        return json_response['status']

def create_sddcvcdr(token, org, name, cidr, provider, subnetId, region, numHost, networkSegment):
    headers = {'csp-auth-token': token,
               'Content-Type': 'application/json', 'Accept': 'application/json'}
    connectedAccount = get_connected_account(org, token)
    data = {
        'name': name,
        'account_link_sddc_config': [
            {
                'customer_subnet_ids': [
                    subnetId
                ],
                'connected_account_id': connectedAccount
            }
        ],
        'vpc_cidr': cidr,
        'provider': provider.upper(),
        'sso_domain': 'vmc.local',
        'num_hosts': numHost,
        'sddc_type': 'DEFAULT',
        'deployment_type': 'SingleAZ',
        'size': 'large',
        'vxlan_subnet': networkSegment,
        'region': region
    }
    resp = requests.post('https://vmc.vmware.com/vmc/api/orgs/{orgId}/sddcs'.format(
        orgId=org), json=data, headers=headers)
    json_response = resp.json()
    print(name + ' SDDC ' + str(json_response['status']))
    if json_response['status'] not in (400, 500):
        return json_response['id']
    else:
        return json_response['status']

def deploy_hcx(token, sddcId):
    data = {'token': token, 'Content-Type': 'application/json'}
    resp = requests.post(
        'https://connect.hcx.vmware.com/provider/csp/api/sessions', json=data)
    hcxAuthToken = resp.headers.get('x-hm-authorization')
    headers = {'x-hm-authorization': hcxAuthToken,
               'Content-Type': 'application/json', 'Accept': 'application/json'}

    resp = requests.post('https://connect.hcx.vmware.com/provider/csp/consumer/api/sddcs/{sddc}?action=activate'.format(
        sddc=sddcId), headers=headers)
    if (resp.status_code == 200):
        json_response = resp.json()
        print(json_response)
    else:
        print('HCX Deployment Failed')
        print(resp.json()['message'])

def status_hcx(token, sddcId):
    data = {'token': token, 'Content-Type': 'application/json'}
    resp = requests.post(
        'https://connect.hcx.vmware.com/provider/csp/api/sessions', json=data)
    hcxAuthToken = resp.headers.get('x-hm-authorization')
    headers = {'x-hm-authorization': hcxAuthToken,
               'Content-Type': 'application/json', 'Accept': 'application/json'}

    resp = requests.post('https://connect.hcx.vmware.com/provider/csp/consumer/api/sddcs/{sddc}?action=getStatus'.format(
        sddc=sddcId), headers=headers)
    if (resp.status_code == 200):
        json_response = resp.json()
        return json_response['deploymentStatus'] + ' ' + json_response['state']
    else:
        # print('HCX Deployment Failed')
        print(resp.json()['message'])

def get_task(sddcName, orgId, token, task_id):
    headers = {'csp-auth-token': token, 'Accept': 'application/json'}
    resp = requests.get('https://vmc.vmware.com/vmc/api/orgs/{orgId}/tasks/{task_id}'.format(
        orgId=orgId, task_id=task_id), headers=headers)
    task = json.loads(resp.text)
    print(sddcName, task['status'],
          task['phase_in_progress'], task['progress_percent'])


def get_connected_account(orgId, token):
    headers = {'csp-auth-token': token, 'Accept': 'application/json'}
    resp = requests.get(
        'https://vmc.vmware.com/vmc/api/orgs/{orgId}/account-link/connected-accounts'.format(orgId=orgId), headers=headers)
    results = json.loads(resp.text)
    for cId in results:
        return cId['id']


def list_users(csp, token, org):
    headers = {'csp-auth-token': token,
               'Content-Type': 'application/json', 'Accept': 'application/json'}
    # params = {'orgID': org}
    # resp = requests.get('{host}/csp/gateway/am/api/orgs/{orgId}/users'.format(
    resp = requests.get('{host}/csp/gateway/am/api/v2/orgs/{orgId}/users'.format(
        host=csp, orgId=org), headers=headers)
    orgdata = resp.json()
    return(orgdata['results'])


def add_user(csp, token, org, user, vcdr):
    headers = {'csp-auth-token': token,
               'Content-Type': 'application/json', 'Accept': 'application/json'}
    params = {'orgID': org}
    vmcJSON = {
            'serviceDefinitionLink': '/csp/gateway/slc/api/definitions/external/ybUdoTC05kYFC9ZG560kpsn0I8M_',
            'serviceRoleNames': ['vmc-user:full', 'nsx:cloud_admin']
        }
    logJSON = {
        'serviceDefinitionLink': '/csp/gateway/slc/api/definitions/external/7cJ2ngS_hRCY_bIbWucM4KWQwOo_',
        'serviceRoles': [{
            'name': 'log-intelligence:admin',
            "resource": "instance:76acd0b7-469c-4ff8-b87b-8649b8c645b6"
        }]
    }
    vcdrJSON = {
            'serviceDefinitionLink':	"/csp/gateway/slc/api/definitions/paid/0e455237-1d3a-4e03-b231-f29f57eaade2",
            'serviceRoleNames': ['vcdr:administrator', 'vcdr:console-admin']
        }

    data = {
        'usernames': [user],
        'organizationRoles': [
            {'name': 'org_member'},
            {'name': 'support_user'},
            {'name': 'developer'}
        ],
        'serviceRolesDtos': [
        ]
    }
    if vcdr:
        data['serviceRolesDtos'].append(vcdrJSON)
        data['serviceRolesDtos'].append(vmcJSON)
    else:
        data['serviceRolesDtos'].append(logJSON)
        data['serviceRolesDtos'].append(vmcJSON)
    resp = requests.post('{host}/csp/gateway/am/api/orgs/{orgId}/invitations'.format(
        host=csp, orgId=org), json=data, headers=headers)
    return(resp)


def remove_user(csp, token, org, user):
    headers = {'csp-auth-token': token,
               'Content-Type': 'application/json', 'Accept': 'application/json'}
    params = {'orgID': org}
    data = {
        'email': user
    }
    resp = requests.patch('{host}/csp/gateway/am/api/orgs/{orgId}/users'.format(
        host=csp, orgId=org), json=data, headers=headers)
    return(resp)

# ============================
# SDDC - TKG
# ============================

def get_sddc_id(orgID, token, sddc_name):
    myHeader = {'csp-auth-token': token}
    myURL = f"https://vmc.vmware.com/vmc/api/orgs/" + orgID + "/sddcs"
    response = requests.get(myURL, headers=myHeader)
    jsonResponse = response.json()
    for i in range(len(jsonResponse)):
        if jsonResponse[i]['name'] == sddc_name:
            sddc_id = jsonResponse[i]['id']
            return sddc_id


def get_cluster_id(org_id, sddc_id, session_token):
    myHeader = {'csp-auth-token': session_token}
    myURL = "https://vmc.vmware.com/vmc/api/orgs/{}/sddcs/{}".format(org_id, sddc_id)
    response = requests.get(myURL, headers=myHeader)
    json_response = response.json()
    # pretty_data = json.dumps(response.json(), indent=4)
    # print(pretty_data)
    cluster_id = json_response['resource_config']['clusters'][0]['cluster_id']
    return cluster_id

def validate_cluster(org_id, sddc_id, cluster_id, session_token):
    myHeader = {'csp-auth-token': session_token}
    myURL = "https://vmc.vmware.com/api/wcp/v1/orgs/{}/deployments/{}/clusters/{}/operations/validate-cluster".format(org_id, sddc_id, cluster_id)
    body = {
        # no need for a body
    }
    response = requests.post(myURL, json=body, headers=myHeader)
    json_response = response.json()
    # pretty_data = json.dumps(response.json(), indent=4)
    # print(pretty_data)
    task_id = json_response ['id']
    return task_id

def validate_network( org_id, sddc_id, cluster_id, session_token, egress_CIDR, ingress_CIDR,namespace_CIDR, service_CIDR):
    myHeader = {'csp-auth-token': session_token}
    myURL = "https://vmc.vmware.com/api/wcp/v1/orgs/{}/deployments/{}/clusters/{}/operations/validate-network".format(org_id, sddc_id, cluster_id)
    body = {
        "egress_cidr": [egress_CIDR],
        "ingress_cidr": [ingress_CIDR],
        "namespace_cidr": [namespace_CIDR],
        "service_cidr": service_CIDR
    }
    response = requests.post(myURL, json=body, headers=myHeader)
    json_response = response.json()
    # pretty_data = json.dumps(response.json(), indent=4)
    # print(pretty_data)
    task_id = json_response ['id']
    return task_id

def enable_wcp( org_id, sddc_id, cluster_id, session_token, egress_CIDR, ingress_CIDR,namespace_CIDR, service_CIDR):
    myHeader = {'csp-auth-token': session_token}
    myURL = "https://vmc.vmware.com/api/wcp/v1/orgs/{}/deployments/{}/clusters/{}/operations/enable-wcp".format(org_id, sddc_id, cluster_id)
    body = {
        "egress_cidr": [egress_CIDR],
        "ingress_cidr": [ingress_CIDR],
        "namespace_cidr": [namespace_CIDR],
        "service_cidr": service_CIDR
    }
    response = requests.post(myURL, json=body, headers=myHeader)
    json_response = response.json()
    # pretty_data = json.dumps(response.json(), indent=4)
    # print(pretty_data)
    task_id = json_response ['id']
    return task_id

def disable_wcp( org_id, sddc_id, cluster_id, session_token):
    myHeader = {'csp-auth-token': session_token}
    myURL = "https://vmc.vmware.com/api/wcp/v1/orgs/{}/deployments/{}/clusters/{}/operations/disable-wcp".format(org_id, sddc_id, cluster_id)
    body = {
        # no need for a body
    }
    response = requests.post(myURL, json=body, headers=myHeader)
    json_response = response.json()
    # pretty_data = json.dumps(response.json(), indent=4)
    # print(pretty_data)
    task_id = json_response ['id']
    return task_id

