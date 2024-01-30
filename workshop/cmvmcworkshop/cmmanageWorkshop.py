#! /usr/bin/python

from sddc_import_export import main
from cmmanageSDDC import *
from cmmanageAWS import *
from vraccleanup import *
from cloudaccount import *
from os.path import join, dirname
from dotenv import load_dotenv
from threading import Thread
import logging
import argparse
import sys
import os
import json
import time
import requests


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def get_args():
    parser = argparse.ArgumentParser(description='VMC Expert SDDC Manager')
    parser.add_argument('--csp', help='csp host',
                        default='https://console.cloud.vmware.com')
    parser.add_argument('--profile', '-f', required=True,
                        help='AWS Profile Name')
    parser.add_argument('--region', '-r', required=False,
                        help='AWS region to deploy to')
    parser.add_argument('--cmd', '-c', required=True,
                        help='create, delete, delete-group, status, adduser, removeuser, etc')
    parser.add_argument('--org', '-o', required=False,
                        help='Org name or all')
    parser.add_argument('--sddc', '-s', required=False,
                        help='SDDC name or all')
    parser.add_argument('--pwd', '-p', required=False,
                        help='Password for AWS Services')
    parser.add_argument('--email', '-e', required=False,
                        help='email to add or remove')
    parser.add_argument('--provider', '-z', required=False,
                        help='Use ZEROCLOUD for testing SDDCs')

    return parser.parse_args()


def send_email(email, subject, body):
    url = os.getenv('flow_url')
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    data = {
        'emailAddress': email,
        'emailSubject': subject,
        'emailBody': body,
    }
    resp = requests.post(url, json=data, headers=headers)


if __name__ == "__main__":
    # enable logging
    logname = './logs/workshop.log'
    loglevel = logging.INFO
    logging.basicConfig(filename=logname,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=loglevel)

    args = get_args()
    # profile name configured in awscli
    emailTo = os.getenv('email_to')
    profileName = args.profile
    regionName = args.region
    cmd = args.cmd
    if args.org:
        orgName = args.org.upper().split(',')
    else:
        orgName = ''
    if args.sddc:
        sddc = args.sddc.upper().split(',')
    else:
        sddc = ''
    password = args.pwd
    provider = args.provider
    csp = args.csp
    email = args.email
    jsonConfig = '../json/{profile}.json'.format(profile=profileName)
    regionURL = {
        'us-east-1': 's3.amazonaws.com',
        'us-west-2': 's3-us-west-2.amazonaws.com',
        'eu-central-1': 's3.eu-central-1.amazonaws.com'
    }
    vmcRegion = {
        'us-east-1': 'US_EAST_1',
        'us-west-2': 'US_WEST_2',
        'eu-central-1': 'EU_CENTRAL_1',
        'ap-southeast-2': 'AP_SOUTHEAST_2'
    }
    yamlURL = 'https://{profile}-{region}-cf.{url}/'.format(
        profile=profileName, region=regionName, url=regionURL[regionName])

    boto3.setup_default_session(
        profile_name=profileName, region_name=regionName)
    f = open(jsonConfig)
    with open(jsonConfig, 'r') as f:
        data = json.load(f)

    # upload latest yaml files to s3
    ymlFiles = {
        'cmworkshop-main.yml',
        'cmworkshop-infra.yml',
        'cmworkshop-services.yml'
    }
    bucketName = '{profile}-{region}-cf'.format(
        profile=profileName, region=regionName)
    for f in ymlFiles:
        upload_file(f, bucketName)

    # test output
    if cmd == 'test':
        for i in data:
            org = i['OrgName']
            orgId = i['OrgId']
            if org.upper() in orgName or 'ALL' in orgName:
                print(orgId)

    # add users to orgs
    if cmd == 'adduser' or cmd == 'removeuser' or cmd == 'listusers':
        for i in data:
            org = i['OrgName']
            rToken = i['RefreshToken']
            orgId = i['OrgId']
            if (email):
                # addUsers = email
                totalUsers = email.split(',')
            else:
                totalUsers = i['Users']
            if 'VCDR' in org:
                vcdrOpt = True
            else:
                vcdrOpt = False
            for user in totalUsers:
                if org.upper() in orgName or 'ALL' in orgName:
                    if cmd == 'adduser':
                        resp = add_user(csp, get_token(
                            csp, rToken), orgId, user, vcdrOpt)
                        if resp.status_code == 202:
                            print('Added user', user, 'to', org)
                        else:
                            print('Failed adding', user)
                            print(resp.text)
                    if cmd == 'removeuser':
                        resp = remove_user(csp, get_token(
                            csp, rToken), orgId, user)
                        if resp.status_code == 200:
                            print('Removed user', user, 'from', org)
                        else:
                            print('Failed removing', user)
                    if cmd == 'listusers':
                        resp = list_users(csp, get_token(
                            csp, rToken), orgId)
                        for users in resp:
                            print(users['user']['username'],
                                  users['organizationRoles'][0]['name'],
                                  'on', org)
                        break

    if cmd == 'cmcreate':
        # Manage AWS infrastructure
        taskId = []
        send_email(emailTo, profileName.upper() + ' ' + ''.join(orgName) +
                    ' Deployment Started', 'Thanks,<br>Skyler')
        while True:
            for i in range(len(data) - 1, -1, -1):
                deleteOrg = False
                org = data[i]['OrgName']
                rToken = data[i]['RefreshToken']
                orgId = data[i]['OrgId']
                awsConfig = data[i]['awsConfig']
                sddcConfig = data[i]['sddcConfig']
                for a in range(len(awsConfig) - 1, -1, -1):
                    # aws config
                    awsVPC1 = awsConfig[a]['awsVPC1']
                    awsVPC2 = awsConfig[a]['awsVPC2']
                    stackName = awsConfig[a]['stackName']
                    subnet1 = awsConfig[a]['awsSubnet1']
                    subnet2 = awsConfig[a]['awsSubnet2']
                    subnet3 = awsConfig[a]['awsSubnet3']
                    subnet4 = awsConfig[a]['awsSubnet4']
                    # sddc config
                    sddcName = sddcConfig[a]['SDDCName']
                    cidr = sddcConfig[a]['CIDR']
                    region = vmcRegion[regionName]
                    numHost = sddcConfig[a]['NumHosts']
                    SDDCnum = sddcConfig[a]['SDDCnum']
                    networkSeg = sddcConfig[a]['NetworkSegment']
                    if org in orgName or 'ALL' in orgName or 'ALL' in sddc or sddcName.upper() in sddc:
                        if cmd == 'cmcreate':
                            stackStatus = status_aws_env(
                                stackName, stackName, False)
                            if stackStatus == 'CREATE_FAILED' or stackStatus == 'DELETE_FAILED':
                                print(stackName, delete_aws_env(stackName))
                            elif stackStatus == 'Stack doesn\'t exist':
                                if 'VCDR' in sddcName:
                                    vcdrOpt = 'True'
                                else:
                                    vcdrOpt = 'False'
                                cmcreate_aws_infra(yamlURL, profileName, stackName, password,
                                                 awsVPC1, awsVPC2, subnet1, subnet2, subnet3, subnet4, vcdrOpt)
                                print(stackName, 'Deploying AWS Stack')
                                # space out aws deployments
                                sleep(10)
                            elif stackStatus == 'CREATE_COMPLETE':
                                sddcStatus = status_sddc(
                                    get_token(csp, rToken), orgId, sddcName, False)
                                if (sddcStatus):
                                    # print('VMC SDDC:', sddcStatus['name'],
                                    #       '-', sddcStatus['sddc_state'])
                                    for task in taskId:
                                        if sddcName == task['name']:
                                            get_task(sddcName, orgId, get_token(
                                                csp, rToken), task['task_id'])
                                    if sddcStatus['sddc_state'] == 'FAILED':
                                        remove_sddc(
                                            get_token(csp, rToken), orgId, sddcName)
                                    if sddcStatus['sddc_state'] == 'READY':
                                        awsConfig.remove(awsConfig[a])
                                        sddcConfig.remove(sddcConfig[a])
                                        print(sddcName, 'removed from list')
                                else:
                                    subnetId = get_aws_subnet_id(sddcName)
                                    subnetId1 = get_aws_subnet_id1(sddcName)
                                    token = get_token(csp, rToken)
                                    if (subnetId):
                                        if SDDCnum % 2:
                                            resp = create_sddc(token, orgId, sddcName,
                                                            cidr, provider, subnetId, region, numHost, networkSeg)
                                        else:
                                            resp = create_sddc(token, orgId, sddcName,
                                                            cidr, provider, subnetId1, region, numHost, networkSeg)
                                        if resp != 400:
                                            taskId.append(
                                                {'name': sddcName, 'task_id': resp})
                    elif any(item.startswith('VMC') for item in orgName):
                        deleteOrg = True
                    elif any(item.startswith('VMCEXPERT') for item in orgName):
                        awsConfig.remove(awsConfig[a])
                        sddcConfig.remove(sddcConfig[a])
                if len(awsConfig) == 0:
                    data.remove(data[i])
                elif deleteOrg == True:
                    data.remove(data[i])
            if len(data) == 0:
                break
            time.sleep(60)
        print(cmd, 'complete')
        send_email(emailTo, profileName.upper() + ' ' + ''.join(orgName) +
                   ' Deployment is Complete', 'Thanks,<br>Skyler')
# duplicated to vmcworkshop, but could be useful to have it here
    if cmd == 'status-sddc':
        results = ''
        for s in data:
            org = s['OrgName']
            rToken = s['RefreshToken']
            orgId = s['OrgId']
            if org.upper() in orgName or 'ALL' in orgName or 'ALL' in sddc:
                if cmd == 'status-sddc':
                    resp = []
                    resp = status_sddc(
                    get_token(csp, rToken), orgId, '', True)
                    if (resp):
                        for r in resp:
                            results = results + 'orgId' + '-' + r['org_id'] + ' ' + 'VMC SDDC:' + r['name'] + '-' + r['id'] + '-' + r['sddc_state'] + ' ' + r['resource_config']['availability_zones'][0] + '<br>'
        send_email(emailTo, profileName.upper() + ' ' + ''.join(orgName) +
            ' SDDC', results + '<br>Thanks,<br>Skyler')

    if cmd == 'delete' or cmd == 'status' or cmd == 'create-route':
        # delete sddc first
        results = ''
        for s in data:
            org = s['OrgName']
            rToken = s['RefreshToken']
            orgId = s['OrgId']
            for i in s['sddcConfig']:
                sddcName = i['SDDCName']
                if (not provider):
                    provider = i['Provider']
                if org.upper() in orgName or 'ALL' in orgName or 'ALL' in sddc or sddcName.upper() in sddc:
                    if cmd == 'delete':
                        if 'ALL' in orgName:
                            sddcName = 'ALL'
                        remove_sddc(get_token(csp, rToken), orgId, sddcName)
                    if cmd == 'status':
                        resp = status_sddc(
                            get_token(csp, rToken), orgId, sddcName, False)
                        resp_group = sddc_group(
                            get_token(csp, rToken), orgId, False)
                        if (resp):
                            print(org, 'VMC SDDC:', resp['name'],
                                  '-', resp['sddc_state'], resp['resource_config']['availability_zones'][0])
                        else:
                            print('VMC SDDC:', sddcName, 'doesn\'t exist')
        # sleep some before moving to AWS
        if cmd == 'delete':
            send_email(emailTo, profileName.upper() + ' ' + ''.join(orgName) +
                      ' is being deleted', 'Thanks,<br>Skyler')
            time.sleep(60)

        # delete AWS infrastructure
        for i in data:
            org = i['OrgName']
            rToken = i['RefreshToken']
            orgId = i['OrgId']
            for aws in i['awsConfig']:
                stackName = aws['stackName']
                awsVPC1 = aws['awsVPC1']
                if org.upper() in orgName or 'ALL' in orgName or 'ALL' in sddc or stackName.upper() in sddc:
                    if cmd == 'delete':
                        print(stackName, delete_aws_env(stackName))
                    if cmd == 'status':
                        print('AWS Services: ' + stackName + ' Infra: ' + status_aws_env(
                            stackName, 'InfraStack', False), 'Services:', status_aws_env(stackName, 'ServiceStack', False))
                    if cmd == 'create-route':
                        create_default_route(stackName, awsVPC1)

    if cmd == 'prepsddc':
        # prep firewall SDDC
        for i in data: 
            org = i['OrgName']
            rToken = i['RefreshToken']
            orgId = i['OrgId']
            if org.upper() in orgName or 'ALL' in orgName:
                # getNSXTproxy(csp, org, orgId, listsddcid(get_token(csp, rToken), csp, org,))
                # listsddcid(get_token(csp, rToken), csp, org)

                 newSDDCMGWRule(getNSXTproxy(csp, org, orgId, listsddcid(get_token(csp, rToken),
                        csp, org,)),get_token(csp, rToken), )

    if cmd == 'vraccleanup' or cmd == 'create-vrac':
        for i in data:
                org = i['OrgName']
                rToken = i['RefreshToken']
                orgId = i['OrgId']            
                if org.upper() in orgName or 'ALL' in orgName:
                    if cmd == 'vraccleanup':
                        cleanup(get_token(csp, rToken), rToken)
                    if cmd == 'create-vrac':
                        region = args.region 
                        aws_key_id = i['aws_key_id']
                        aws_access_key = i['aws_access_key']   
                        create_aws_ca(get_token(csp, rToken), aws_key_id, aws_access_key, region, org)