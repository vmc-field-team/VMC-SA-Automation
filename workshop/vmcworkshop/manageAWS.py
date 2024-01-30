#! /usr/bin/python
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def status_aws_env(stackName, stackEvent, getARN):
    client = boto3.client('cloudformation')
    try:
        response = client.describe_stack_events(
            StackName=stackName
        )
        for stack in response['StackEvents']:
            if stack['LogicalResourceId'] == stackEvent:
                if stack['ResourceStatus'] == 'CREATE_COMPLETE' or stack['ResourceStatus'] == 'DELETE_IN_PROGRESS' or stack['ResourceStatus'] == 'CREATE_FAILED':
                    if getARN:
                        results = stack['PhysicalResourceId']
                        break
                    else:
                        results = stack['ResourceStatus']
                        break
            results = stack['ResourceStatus']
    except:
        results = 'Stack doesn\'t exist'
    return results


def get_aws_subnet_id(stackName):
    arn = status_aws_env(stackName, 'InfraStack', True)
    client = boto3.client('cloudformation')
    response = client.describe_stacks(
        StackName=arn
    )
    if response['Stacks'][0]['Outputs'][3]['OutputValue']:
        return response['Stacks'][0]['Outputs'][3]['OutputValue']

def get_aws_subnet_id1(stackName):
    arn = status_aws_env(stackName, 'InfraStack', True)
    client = boto3.client('cloudformation')
    response = client.describe_stacks(
        StackName=arn
    )
    # print(response['Stacks'][0]['Outputs'][5]['OutputValue'])
    if response['Stacks'][0]['Outputs'][5]['OutputValue']:
        return response['Stacks'][0]['Outputs'][5]['OutputValue']


def delete_aws_env(stackName):
    client = boto3.client('cloudformation')
    try:
        response = client.delete_stack(
            StackName=stackName
        )
        results = 'Deleting'
    except:
        results = 'Stack doesn\'t exist'
    return results


def create_default_route(stackName, cidr):
    client = boto3.client('ec2')
    response = client.describe_route_tables(
        Filters=[
            {
                'Name': 'route.destination-cidr-block',
                'Values': [
                    cidr,
                ]
            }
        ]
    )
    rtb = response['RouteTables'][0]['Associations'][0]['RouteTableId']

    response = client.describe_internet_gateways(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    stackName + ' IGW',
                ]
            }
        ]
    )
    igw = response['InternetGateways'][0]['InternetGatewayId']

    response = client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw,
        RouteTableId=rtb,
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(stackName, 'default route added')
    else:
        print(stackName, 'default route failed')

def get_aws_vcdr_subnet_id(stackName, scfs_az):
    client = boto3.client('ec2')

    response = client.describe_subnets(
        Filters=[
            {
                'Name': 'availability-zone-id',
                'Values': [
                    scfs_az,
                ],
            },
        ],
    )

    for subnet in response['Subnets']:
        for tag in subnet['Tags']:
            if tag['Key'] == 'Name' and tag['Value'] == stackName:
                return subnet['SubnetId']

def create_aws_infra(yamlURL, profileName, stackName, password, vpcCIDR1, vpcCIDR2, subnet1, subnet2, subnet3, subnet4, vcdr):
    client = boto3.client('cloudformation')

    params = [
        {
            'ParameterKey': 'EnvironmentName',
            'ParameterValue': stackName
        },
        {
            'ParameterKey': 'StudentPassword',
            'ParameterValue': password
        },
        {
            'ParameterKey': 'Profile',
            'ParameterValue': profileName
        },
        {
            'ParameterKey': 'yamlURL',
            'ParameterValue': yamlURL
        },
        {
            'ParameterKey': 'vpcCIDR1',
            'ParameterValue': vpcCIDR1
        },
        {
            'ParameterKey': 'vpcCIDR2',
            'ParameterValue': vpcCIDR2
        },
        {
            'ParameterKey': 'Subnet1CIDR',
            'ParameterValue': subnet1
        },
        {
            'ParameterKey': 'Subnet2CIDR',
            'ParameterValue': subnet2
        },
        {
            'ParameterKey': 'Subnet3CIDR',
            'ParameterValue': subnet3
        },
        {
            'ParameterKey': 'Subnet4CIDR',
            'ParameterValue': subnet4
        },
        {
            'ParameterKey': 'VCDR',
            'ParameterValue': vcdr
        }
    ]
    response = client.create_stack(
        StackName=stackName,
        Capabilities=['CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND'],
        TemplateURL=yamlURL + 'workshop-main.yml',
        Parameters=params,
        OnFailure='DO_NOTHING'
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        results = 'Success'
    else:
        results = 'Failed'
    return results
