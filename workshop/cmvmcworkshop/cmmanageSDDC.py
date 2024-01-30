#!/usr/bin/env python

import json
import requests
import traceback
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
    vropsJSON = {
            'serviceDefinitionLink':	"/csp/gateway/slc/api/definitions/external/c3cd6561-00d8-49af-807e-257cf626c0c4",
            'serviceRoleNames': ['vrops:admin']
        }
    catalogJSON = {
            'serviceDefinitionLink':	"/csp/gateway/slc/api/definitions/external/Yw-HyBeQzjCXkL2wQSeGwauJ-mA_",
            'serviceRoleNames': ['catalog:admin']
        }
    automationJSON = {
            'serviceDefinitionLink':	"/csp/gateway/slc/api/definitions/external/Zy924mE3dwn2ASyVZR0Nn7lupeA_",
            'serviceRoleNames': ['automationservice:cloud_admin']
        }
    codeJSON = {
            'serviceDefinitionLink':	"/csp/gateway/slc/api/definitions/external/ulvqtN4141beCT2oOnbj-wlkzGg_",
            'serviceRoleNames': ['CodeStream:developer']
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
        data['serviceRolesDtos'].append(vropsJSON)
        data['serviceRolesDtos'].append(catalogJSON)
        data['serviceRolesDtos'].append(automationJSON)
        data['serviceRolesDtos'].append(codeJSON)
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

def getNSXTproxy(csp, org, sddcId, token):
    # Gets the Reverse Proxy URL
    myHeader = {'csp-auth-token': token}
    myURL = "{host}/vmc/api/orgs/{org}/sddcs/{sddcId}".format(host=csp, org=org, sddcId=sddcId)
    response = requests.get(myURL, headers=myHeader)
    json_response = response.json()
    proxy_url = json_response['resource_config']['nsx_api_public_endpoint_url']
    return proxy_url

def newSDDCMGWRule(proxy_url, token, display_name, source_groups, destination_groups, services, action, sequence_number):
    myHeader = {'csp-auth-token': token}
    myURL = (proxy_url + "/policy/api/v1/infra/domains/mgw/gateway-policies/default/rules/" + display_name)
    json_data = {
    "action": action,
    "destination_groups": destination_groups,
    "direction": "IN_OUT",
    "disabled": False,
    "display_name": display_name,
    "id": display_name,
    "ip_protocol": "IPV4_IPV6",
    "logged": False,
    "profiles": [ "ANY" ],
    "resource_type": "Rule",
    "scope": ["/infra/labels/mgw"],
    "services": services,
    "source_groups": source_groups,
    "sequence_number": sequence_number
    }
    response = requests.put(myURL, headers=myHeader, json=json_data)
    json_response_status_code = response.status_code
    return json_response_status_code

def newSDDCCGWRule(proxy_url, token, display_name, source_groups, destination_groups, services, action, scope, sequence_number):
    myHeader = {'csp-auth-token': token}
    myURL = (proxy_url + "/policy/api/v1/infra/domains/cgw/gateway-policies/default/rules/" + display_name)
    json_data = {
    "action": action,
    "destination_groups": destination_groups,
    "direction": "IN_OUT",
    "disabled": False,
    "display_name": display_name,
    "id": display_name,
    "ip_protocol": "IPV4_IPV6",
    "logged": False,
    "profiles": [ "ANY" ],
    "resource_type": "Rule",
    "scope": scope,
    "services": services,
    "source_groups": source_groups,
    "sequence_number": sequence_number
    }
    response = requests.put(myURL, headers=myHeader, json=json_data)
    json_response_status_code = response.status_code
    return json_response_status_code

def listsddcid(token, csp, org):
    headers = {'csp-auth-token': token, 'Accept': 'application/json'}
    resp = requests.post('{host}/vmc/api/orgs/{orgId}/sddcs'.format(
        host=csp, orgId=org),headers = headers)
    if (resp.status_code == 200):
        for id in resp.json():
            json_response = resp.json()
            print(json_response[id])
    else:
        print('no SDDC found')


def getsddcid(token, org, name):
    headers = {'csp-auth-token': token, 'Accept': 'application/json'}
    params = {'orgID': org}
    resp = requests.get(
        'https://vmc.vmware.com/vmc/api/orgs/{orgId}/sddcs'.format(orgId=org), headers=headers)
    orgdata = resp.json()
    for orgs in orgdata:
        for i in orgs['sddc_ID']:
            print(i) 
        else:
            traceback.print_exc('No SDDC')         
#  sddcId = orgs['sddc_id']
        # wait_for_task(org, token, json_response['id'], 60)