#! /usr/bin/python

import json

jsonConfig = '../json/vmcexpert3.json'
f = open(jsonConfig)
with open(jsonConfig, 'r') as f:
    data = json.load(f)

for i in data:
    org = i['OrgName']
    rToken = i['RefreshToken']
    orgId = i['OrgId']
    print(org + ' ' + orgId)
