#!/usr/bin/env python

import json
import requests

from time import sleep
from urllib.parse import urlencode

def get_token(csp, rtoken):
    params = {'refresh_token': rtoken}
    resp = requests.post(
        '{host}/csp/gateway/am/api/auth/api-tokens/authorize'.format(host=csp), params=params)
    return resp.json()['access_token']

def list_users(csp, token, org):
    headers = {'csp-auth-token': token,
               'Content-Type': 'application/json', 'Accept': 'application/json'}
    # params = {'orgID': org}
    # resp = requests.get('{host}/csp/gateway/am/api/orgs/{orgId}/users'.format(
    resp = requests.get('{host}/csp/gateway/am/api/v2/orgs/{orgId}/users'.format(
        host=csp, orgId=org), headers=headers)
    orgdata = resp.json()
    return(orgdata['results'])

token = "" #amer
org = "" #amer
csp = "https://console.cloud.vmware.com"

resp = list_users(csp, get_token(
    csp, token), org)
for users in resp:
    username = users['user']['username'].split('@')
    print(users['user']['firstName'], users['user']['lastName'] + ',' +
        username[0])