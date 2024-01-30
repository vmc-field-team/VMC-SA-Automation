import json
import requests
import time
import argparse
import urllib3
urllib3.disable_warnings()

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []
    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    results = extract(obj, arr, key)
    return results

def get_ca_ids():
    api_url = '{0}/iaas/api/cloud-accounts'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        ca_id = extract_values(json_data,'id')
        return ca_id
    else:
        print(response.status_code)

def get_cs_policies():
    api_url = '{0}/policy/api/policies'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        policy_id = extract_values(json_data,'id')
        return policy_id
    else:
        print(response.status_code)

def delete_policies(policy_ids):
    for x in policy_ids:
        api_url = '{0}/policy/api/policies/{1}'.format(api_url_base,x)
        response = requests.delete(api_url, headers=headers, verify=False)
        if response.status_code == 204:
            print('Successfully Deleted Policy ' + x)
        else:
            print(response.status_code)


def get_deployment_ids():
    api_url = '{0}/deployment/api/deployments'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        ca_id = extract_values(json_data,'id')
        return ca_id
    else:
        print(response.status_code)

def get_cloud_proxy_ids():
    api_url = '{0}/api/data-collector-v2'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        cp_id = extract_values(json_data,'proxyId')
        return cp_id
    else:
        print(response.status_code)

def remove_cloud_proxy(cp_ids):
    if cp_ids:
        for x in cp_ids:
            api_url = '{0}/api/data-collector-v2/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 200:
                print('Successfully Removed Cloud Proxies')
            else:
                print(response.status_code)

def get_blueprint_ids():
    api_url = '{0}/blueprint/api/blueprints'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        ca_id = extract_values(json_data,'id')
        return ca_id
    else:
        print(response.status_code)

def get_action_ids():
    api_url = '{0}/abx/api/resources/actions?page=0&size=20&$filter=system%20eq%20%27false%27'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = extract_values(json_data,'id')
        return obj_id
    else:
        print(response.status_code)

def get_subscription_ids():
    api_url = '{0}/event-broker/api/subscriptions?page=0&size=20&$filter=type%20ne%20%27SUBSCRIBABLE%27'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = extract_values(json_data,'id')
        return obj_id
    else:
        print(response.status_code)

def get_project_ids():
    api_url = '{0}/iaas/api/projects'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = extract_values(json_data,'id')
        return obj_id
    else:
        print(response.status_code)

def get_pipeline_ids():
    api_url = '{0}/pipeline/api/pipelines'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = json_data['links']
        return obj_id
    else:
        print(response.status_code)

def get_content_source_ids():
    api_url = '{0}/catalog/api/admin/sources?search=&size=20&sort=name,asc'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = extract_values(json_data,'id')
        return obj_id
    else:
        print(response.status_code)

def get_cs_webhook_ids():
    api_url = '{0}/pipeline/api/git-webhooks'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = json_data['links']
        return obj_id
    else:
        print(response.status_code)

def get_cs_endpoint_ids():
    api_url = '{0}/pipeline/api/endpoints'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = json_data['links']
        return obj_id
    else:
        print(response.status_code)

def get_secret_ids():
    api_url = '{0}/platform/api/secrets'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = extract_values(json_data,'id')
        return obj_id
    else:
        print(response.status_code)

def delete_secrets(secret_ids):
    if secret_ids:
        for x in secret_ids:
            api_url = '{0}/platform/api/secrets/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Secret with id ' + x)
            else:
                print(response.status_code)

def delete_deployments(bToken, dep_ids):
    if dep_ids:
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer {0}'.format(bToken)}
        for x in dep_ids:
            api_url = '{0}/deployment/api/deployments/{1}/requests'.format(api_url_base,x)
            data =  {
                      "actionId": "Deployment.Delete",
                      "targetId": dep_ids,
                      "inputs": {
                        "ignoreDeleteFailures": "true"
                      }
                    }
            response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
            # print(response)
            if response.status_code == 201:
               print('Successfully Deleted Deployments')
            else:
               print('not yet')
            #    print(response.status_code)

def delete_blueprints(bp_ids):
    if bp_ids:
        for x in bp_ids:
            api_url = '{0}/blueprint/api/blueprints/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Blueprint ' + x)
            else:
                print(response.status_code)

def remove_zones_project(proj_ids):
    if proj_ids:
        for x in proj_ids:
            api_url = '{0}/provisioning/mgmt/project-config'.format(api_url_base)
            data =  {"projectState":{"documentSelfLink":"/provisioning/resources/projects/" + x},"cloudZones":[]}
            response = requests.patch(api_url, headers=headers, data=json.dumps(data), verify=False)
            if response.status_code == 200:
                print('Successfully Removed Zones From Project')
            else:
                print(response.status_code)

def delete_project(proj_ids):
    if proj_ids:
        for x in proj_ids:
            api_url = '{0}/iaas/api/projects/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Project')
            else:
                print(response.status_code)

def delete_subscriptions(sub_ids):
    if sub_ids:
        for x in sub_ids:
            api_url = '{0}/event-broker/api/subscriptions/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Subscription')
            else:
                print(response.status_code)

def delete_actions(action_ids,proj_ids):
    if action_ids:
        for x in action_ids:
            for y in proj_ids:
                api_url = '{0}/abx/api/resources/actions/{1}?projectId={2}'.format(api_url_base,x,y)
                response = requests.delete(api_url, headers=headers, verify=False)
                if response.status_code == 200:
                    print('Successfully Deleted Action')

def delete_cloud_accounts(ca_ids):
    if ca_ids:
        for x in ca_ids:
            api_url = '{0}/iaas/api/cloud-accounts/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Cloud Account')
            else:
                print(response.status_code)

def delete_cs_pipelines(pipe_ids):
    if pipe_ids:
        for x in pipe_ids:
            api_url = '{0}{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 200:
                print('Successfully Deleted Code Stream Pipeline')
            else:
                print(response.status_code)

def delete_content_sources(content_source_ids):
    if content_source_ids:
        for x in content_source_ids:
            api_url = '{0}/catalog/api/admin/sources/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Content Source')

def delete_cs_endpoints(cs_endpoints_ids):
    if cs_endpoints_ids:
        for x in cs_endpoints_ids:
            api_url = '{0}{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 200:
                print('Successfully Deleted Code Stream Endpoint')

def delete_cs_webhooks(cs_webhooks_ids):
    if cs_webhooks_ids:
        for x in cs_webhooks_ids:
            api_url = '{0}{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Code Stream Webhook')

def get_ca_content_sources():
    api_url = '{0}/content/api/sources'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = extract_values(json_data,'id')
        return obj_id
    else:
        print(response.status_code)

def delete_ca_content_sources(ca_content_sources):
    if ca_content_sources:
        for x in ca_content_sources:
            api_url = '{0}/content/api/sources/{1}'.format(api_url_base,x)
            response = requests.delete(api_url, headers=headers, verify=False)
            if response.status_code == 204:
                print('Successfully Deleted Cloud Assembly Content Sources')

def get_provisioning_endpoints():
    api_url = '{0}/provisioning/uerp/provisioning/mgmt/endpoints'.format(api_url_base)
    response = requests.get(api_url, headers=headers, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.content.decode('utf-8'))
        obj_id = json_data['documentLinks']
        return obj_id
    else:
        print(response.status_code)

def delete_provisioning_endpoints(prov_endpoints):
    if prov_endpoints:
        for x in prov_endpoints:
            end_type = get_endpoint_type(x)
            while end_type not in ["aws", "azure", "vsphere", "nsxv", "nsxt"]:
                api_url = '{0}/provisioning/uerp/provisioning/mgmt/endpoints{1}'.format(api_url_base,x)
                response = requests.delete(api_url, headers=headers, verify=False)
                if response.status_code == 200:
                    print('Successfully Deleted Integration')
                    break

def get_endpoint_type(prov_endpoint):
        api_url = '{0}/provisioning/uerp/provisioning/mgmt/endpoints{1}'.format(api_url_base,prov_endpoint)
        response = requests.get(api_url, headers=headers, verify=False)
        if response.status_code == 200:
            json_data = json.loads(response.content.decode('utf-8'))
            obj_id = json_data['endpointType']
            return obj_id
        else:
            print(response.status_code)

def get_tag_links():
        api_url = '{0}/provisioning/uerp/resources/tags?expand&$filter=((key%20ne%20%27__*%27)%20and%20(origins.item%20ne%20%27SYSTEM%27))&$orderby=key%20asc&$skip=0'.format(api_url_base)
        response = requests.get(api_url, headers=headers, verify=False)
        if response.status_code == 200:
            json_data = json.loads(response.content.decode('utf-8'))
            obj_ids = json_data['documentLinks']
            return obj_ids
        else:
            print(response.status_code)

def delete_tags():
    tag_links = get_tag_links()
    for x in tag_links:
        api_url = '{0}/provisioning/uerp{1}'.format(api_url_base,x)
        response = requests.delete(api_url, headers=headers, verify=False)
        if response.status_code == 200:
            print('Successfully Deleted Tag ID' + x)

def get_btoken(reToken):
    url = "https://api.mgmt.cloud.vmware.com/iaas/api/login"
    print(reToken)
    data = {'refreshToken': reToken}
    # headers = { 'Content-Type': 'application/json', 'Accept': 'application/json'}
    response  = requests.post(url, json=data)
    # print(response.json())
    bearerToken = response.json()['token']
    return bearerToken

def cleanup(token, reToken):
    global api_url_base, headers

    api_url_base = "https://api.mgmt.cloud.vmware.com"
    headers = {'Content-Type': 'application/json','Authorization': 'Bearer {0}'.format(token)}

    print('*** Cleaning up Environment ***')
    dep_ids = get_deployment_ids()
    bp_ids = get_blueprint_ids()
    action_ids = get_action_ids()
    proj_ids = get_project_ids()
    sub_ids = get_subscription_ids()
    ca_ids = get_ca_ids()
    pipe_ids = get_pipeline_ids()
    cs_endpoint_ids = get_cs_endpoint_ids()
    content_source_ids = get_content_source_ids()
    cs_webhook_ids = get_cs_webhook_ids()
    policy_ids = get_cs_policies()
    secret_ids = get_secret_ids()
    print("Deleting Policy's from Service Broker")
    delete_policies(policy_ids)
    n = 0
    while True:
        print("Deleting Deployments")
        dep_ids = get_deployment_ids()
        delete_deployments(get_btoken(reToken), dep_ids)
        deps = len(dep_ids)
        print("Still Deleting Deployments")
        time.sleep(10)
        if deps == 0:
            print("All Deployments Deleted")
            break
        elif n <= 100:
            n = n + 1
            print("Running through attempt " + str(n))
        elif n >= 101:
            print("Deleting Deployments Did Not Complete. There are " + str(deps) + " Deployments Not Deleting")
            break
    print("Deleting Blueprints")
    delete_blueprints(bp_ids)
    # time.sleep(10)
    print("Deleting Subscriptions")
    delete_subscriptions(sub_ids)
    # time.sleep(10)
    print("Deleting Actions")
    delete_actions(action_ids,proj_ids)
    # time.sleep(10)
    print("Deleting Secrets")
    delete_secrets(secret_ids)
    # time.sleep(10)
    print("Deleting Cloud Assembly Content Sources")
    ca_content_sources = get_ca_content_sources()
    delete_ca_content_sources(ca_content_sources)
    # time.sleep(10)
#    print("Deleting Cloud Assembly Integrations")
#    prov_end = get_provisioning_endpoints()
#    delete_provisioning_endpoints(prov_end)
#   time.sleep(10)
    print("Deleting Tags in System")
    delete_tags()
    # time.sleep(10)
    print("Deleting Service Broker Content Sources")
    delete_content_sources(content_source_ids)
    # time.sleep(10)
    print("Deleting Code Stream Webhooks")
    delete_cs_webhooks(cs_webhook_ids)
    # time.sleep(10)
    print("Deleting Code Stream Pipelines")
    delete_cs_pipelines(pipe_ids)
    # time.sleep(10)
    print("Deleting Code Stream Endpoints")
    delete_cs_endpoints(cs_endpoint_ids)
    # time.sleep(10)
    print("Deleting Cloud Zones From Projects")
    remove_zones_project(proj_ids)
    # time.sleep(10)
    print("Deleting Projects")
    delete_project(proj_ids)
    # time.sleep(10)
    print("Deleting Cloud Accounts")
    delete_cloud_accounts(ca_ids)
    print("Deleting All Cloud Proxies")
    cp_ids = get_cloud_proxy_ids()
    remove_cloud_proxy(cp_ids)
    # time.sleep(60)
    print("*** Finished Cleanup ***")
