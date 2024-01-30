### Documentation for vRA Cloud API's
# https://www.mgmt.cloud.vmware.com/automation-ui/api-docs/

import json
import requests


def get_token():
    url = "https://api.mgmt.cloud.vmware.com/iaas/api/login"
    payload = "{\n    \"refreshToken\": \"\"\n}"
    headers = { 'Content-Type': 'application/json', 'Host': 'api.mgmt.cloud.vmware.com'}
    authentication  = requests.request("POST", url, headers=headers, data=payload)
    bearerToken = authentication.json()['token']
    return bearerToken

def get_deployments(token):
    """
    Retrieve all deployments and return an array of deployments ID's

    Arguments:

    vRealize Automation Cloud Refresh Token
    """

    api_url =  'https://api.mgmt.cloud.vmware.com/deployment/api/deployments'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    payload = {}
    response = requests.request('GET', api_url, headers=headers, data=payload)
    return response

def delete_deployment(token, deployId):
    """
    Delete deployment by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/deployment/api/deployments/{deployId}?forceDelete=true"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete( api_url, headers=headers)

def get_blueprints(token):
    """
    Retrieve all blueprints that the current logged user has access to
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/blueprint/api/blueprints'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    payload = {}
    response = requests.request('GET', api_url, headers=headers, data=payload)
    return response

def delete_blueprints(token, blueprintId):
    """
    Delete blueprint by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/blueprint/api/blueprints/{blueprintId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete( api_url, headers=headers)


def get_projects(token):
    """
    Retrieve all projects that the current logged user has access to
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/iaas/api/projects'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    payload = {}
    response = requests.request('GET', api_url, headers=headers, data=payload)
    return response

def remove_zones(token, projectId):
    """
    Remove zones from project by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/api/projects/{projectId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    payload = {}
    payload['zoneAssignmentConfigurations'] = []
    response = requests.patch(api_url, headers=headers, data=payload)

def delete_projects(token, projectId):
    """
    Delete projects from project by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/api/projects/{projectId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)

def get_cloudZones(token):
    """
    Get all Cloud Zones
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/iaas/api/zones'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_cloudZones(token, cloudZoneId):
    """
    Delete cloud zonesz by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/api/zones/{cloudZoneId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)

def get_imageProfiles(token):
    """
    Get all Image Profiles
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/iaas/api/image-profiles'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_imageProfile(token, imageProfileId):
    """
    Delete cloud zonesz by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/api/image-profiles/{imageProfileId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)


def get_flavorProfiles(token):
    """
    Get all Image Profiles
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/iaas/api/flavor-profiles'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_flavorProfile(token, flavorProfileId):
    """
    Delete cloud zonesz by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/api/flavor-profiles/{flavorProfileId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)

def get_networkProfiles(token):
    """
    Get all Image Profiles
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/iaas/api/network-profiles'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_networkProfile(token, networkProfileId):
    """
    Delete network profiles by Id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/api/network-profiles/{networkProfileId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)

def get_storageProfiles(token):
    """
    Get all Storage Profiles
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/iaas/api/storage-profiles'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_storageProfile(token, storageProfileId):
    """
    Delete Storage Profile by Id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/api/storage-profiles/{storageProfileId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)

def get_cloudAccounts(token):
    """
    Get all Cloud Accounts
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/iaas/cloud-accounts'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_cloudAccount(token, cloudAccountId):
    """
    Delete Cloud Accounts by Id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/iaas/cloud-accounts/{cloudAccountId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)

def get_subscriptions(token):
    """
    Get all event broker subscriptions
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/event-broker/api/subscriptions'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_subscription(token, subscriptionId):
    """
    Delete all subscriptions by id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/event-broker/api/subscriptions/{subscriptionId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)

def get_abxActions(token):
    """
    Get all ABX actions
    """

    api_url = 'https://api.mgmt.cloud.vmware.com/abx/api/resources/actions/'
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.request('GET', api_url, headers=headers)
    return response

def delete_abxAction(token, abxActionId):
    """
    Delete all ABX Actions by Id
    """

    api_url = f"https://api.mgmt.cloud.vmware.com/abx/api/resources/actions/{abxActionId}"
    headers = {'Content-Type': 'application/json','Authorization': f'Bearer {token}'}
    response = requests.delete(api_url, headers=headers)
#### code block

token = get_token()

## list deployments and then delete it
deployments = get_deployments(token)
deploymentIds = [ i['id'] for i in deployments.json()["content"]]

for x in deploymentIds:
    delete_deployment(token, x)

## list blueprints and then delete it
blueprints = get_blueprints(token)
blueprintIds = [i['id'] for i in blueprints.json()["content"]]

for x in blueprintIds:
    delete_blueprints(token, x)


## list subscriptions from extensibilities, get the id and delete them

subscriptions = get_subscriptions(token)
subscriptionIds = [i['id'] for i in subscriptions.json()["content"]]

for x in subscriptionIds:
    delete_subscription(token, x)

## list abx actions from extensibilities, get the id and delete them

abxActions = get_abxActions(token)
abxActionsIds = [i['id'] for i in abxActions.json()["content"]]

for x in abxActionsIds:
    delete_abxAction(token, x)

## list project, remove the cloud zones from the project and then delete the projects

projects = get_projects(token)
projectsIds = [ i['id'] for i in projects.json()["content"]]

for x in projectsIds:
    remove_zones(token, x)

for x in projectsIds:
    delete_projects(token, x)

## list cloud zones, get cloud zones ids and delete them

cloudZones = get_cloudZones(token)
cloudZonesIds = [i['id'] for i in cloudZones.json()["content"]]

for x in cloudZonesIds:
    delete_cloudZones(token, x)


## list image profiles, get image profile ids and delete them

imageProfiles = get_imageProfiles(token)
imageProfilesId = [i['id'] for i in imageProfiles.json()["content"]]

for x in imageProfilesId:
    delete_imageProfile(token, x)

## list flavor profiles, get flavor profile ids and delete them

flavorProfiles = get_flavorProfiles(token)
flavorProfilesId = [i['id'] for i in flavorProfiles.json()["content"]]

for x in flavorProfilesId:
    delete_flavorProfile(token, x)

## list network profiles, get network profiles ids and delete them

networkProfiles = get_networkProfiles(token)
networkProfilesId = [i['id'] for i in networkProfiles.json()["content"]]

for x in networkProfilesId:
    delete_networkProfile(token, x)

## list storage profiles, get storage profiles ids and delete them

storageProfiles = get_storageProfiles(token)
storageProfilesId = [i['id'] for i in storageProfiles.json()["content"]]

for x in storageProfilesId:
    delete_storageProfile(token, x)

## list cloud accounts, get cloud account ids and delete them

cloudAccounts = get_cloudAccounts(token)
cloudAccountsId = [i['id'] for i in cloudAccounts.json()["content"]]

for x in cloudAccountsId:
    delete_cloudAccount(token, x)
