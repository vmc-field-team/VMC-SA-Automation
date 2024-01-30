import json
import requests
from pickle import FALSE 

def create_aws_ca(token, aws_key_id, aws_access_key, region, org, create_zone="false"):
    """
    Setup and configure AWS Cloud Accounts
    Arguments:
    url = vRA FQDN
    username = vRA admin user
    password = vRA Admin password
    aws_key_id = AWS Key
    aws_access_key = AWS Access Key
    name = Name of AWS Integration
    region_name = Name of the region to assign (i.e us-west-1 or 'us-west-1,us-west-2' for multiple regions)
    create_zone = Should vRA create a Cloud Zone for each region (default is true)
    """
    api_url_base = "https://api.mgmt.cloud.vmware.com"
    headers = {'Content-Type': 'application/json','Authorization': 'Bearer {0}'.format(token)}
    api_url = '{0}/iaas/api/cloud-accounts-aws'.format(api_url_base)
    data =  {
                "name": "AWS Cloud Account",
                "description": "AWS Cloud Account for MCM Expert-Workshop ",
                "accessKeyId": aws_key_id,
                "secretAccessKey": aws_access_key,
                "regionIds": [region],
                "createDefaultZones": create_zone,
            }
    response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == 201:
        print('Successfully Created AWS Cloud Account for ' + org)
        json_data = json.loads(response.content.decode('utf-8'))
        return json_data
    else:
        print(response.status_code)
        json_data = json.loads(response.content.decode('utf-8'))
        return json_data
        