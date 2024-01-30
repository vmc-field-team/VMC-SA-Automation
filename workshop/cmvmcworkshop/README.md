# VMC Lab Deployment Guide

This page is your guide to setting up and running a customer experience day for the VMware Cloud on AWS solution. Follow this guide in order to successfully complete a customer experience day. If you find any errors on this page or you feel there is something which can be improved, please feel empowered to make the required changes. We are constantly looking to improve this program. If you have anything which you think would be good to add to this content and help improve the value this program brings to customers, please reach out and bring your ideas to the attention of the #vmc-workshops channel in Slack.

## Overview

When deploying the lab environment, the scripts use a combination of AWS Cloudformation templates to deploy the AWS network infrastructure and services to support the labs and deploy the VMC on AWS SDDC's using VMC API.

The deployment process will first start with the AWS infrastructure (VPC and subnets).  Once complete, the SDDC will begin deploying and then the  AWS services (EFS, xfS, AD, RDS, etc.).  The total time to deploy can approximately 90 minutes to 2 hours.

The delete process is very similar to the deployment process and will undo everything deployed to take it back to a clean environment.

## Requirements

Latest verion of Python is required to run these commands.  PIP is also used to install the additional requirements in order to run the commands successfully.
`python3 -m pip install -r requirements.txt`

Boto3 is used to interact with AWS to deploy the CloudFormation templates.  Refer to the boto3 documentation for more information [here](https://pypi.org/project/boto3/).

Optionally you can run this in a docker container.
`docker build -t vmclab:latest .`
`docker run -i -w /tmp/scripts/skyler/vmcworkshop -v $HOME/.aws/credentials:/root/.aws/credentials:ro -v $HOME/.aws/config:/root/.aws/config -v /git/hank:/tmp/scripts vmcworkshop:latest python3 manageWorkshop.py --profile $1 --region $2 --cmd deploy-hcx --org $3`

## Configure the JSON file

The example below shows the configuration for one VMC on AWS org and two SDDC's.  **Note** all fields are required.

First section provides the org name, org id and refresh token.  The *sddcConfig* provides the required properties to deploy a SDDC.  The *awsConfig* provides the required properties to deploy the AWS infrastructure.

```[
    {
      "OrgName": "VMCEXPERT1-01",
      "OrgId": "",
      "Orgnum": 1,
      "RefreshToken": "",
      "aws_key_id": "",
      "aws_access_key": "",
      "sddcConfig": [
            {
                "SDDCName": "VMCEXPERT2-01",
                "Provider": "AWS",
                "CIDR": "10.101.0.0/20",
                "NetworkSegment": "192.168.101.0/24",
                "NetworkGateway": "10.10.101.1/24",
                "DHCPRange": "10.10.101.100-10.10.101.200",
                "NumHosts": 1,
                "Region": "US_WEST_2"
            },
            {
                "SDDCName": "VMCEXPERT2-02",
                "Provider": "AWS",
                "CIDR": "10.102.0.0/20",
                "NetworkSegment": "192.168.102.0/24",
                "NetworkGateway": "10.10.102.1/24",
                "DHCPRange": "10.10.102.100-10.10.102.200",
                "NumHosts": 1,
                "Region": "US_WEST_2"
            }
        ],
        "awsConfig": [
            {
                "stackName": "VMCEXPERT2-01",
                "awsVPC1": "172.101.0.0/16",
                "awsSubnet1": "172.101.0.0/20",
                "awsSubnet2": "172.101.16.0/20",
                "awsVPC2": "10.101.16.0/20",
                "awsSubnet3": "10.101.16.0/24",
                "awsSubnet4": "10.101.17.0/24"
            },
            {
                "stackName": "VMCEXPERT2-02",
                "awsVPC1": "172.102.0.0/16",
                "awsSubnet1": "172.102.0.0/20",
                "awsSubnet2": "172.102.16.0/20",
                "awsVPC2": "10.102.16.0/20",
                "awsSubnet3": "10.102.16.0/24",
                "awsSubnet4": "10.102.17.0/24"
            }
        ],
        "Users": [
            "ced01@vmware-hol.com",
            "ced02@vmware-hol.com"
        ]
    }
]
```

## AWS CloudFormation Templates

Three yaml files are used to deploy the AWS infrastructure and services.  The *main* yaml file is used to gather the parameters and pass to the *infrastructure* yaml and *services* yaml.  The reason for having this split into two separate deployments, is to improve the overall deployment time.  The *infrastructure* only takes a few minutes to deploy whereas the *services* can take up to an hour to deploy completely.

The yaml files are stored and executed from S3.  As part of the script, it will upload the yaml files to the designated bucket based on profile and region.  The naming convention for s3 Bucket is {profile name}-{region}-cf.  Example for profile name vmcexpert1 deploying in us-west-2 (Oregon) would be **vmcexpert2-us-west-2-cf**.

Make sure S3 Buckets exist for each profile and region you want to deploy to.

## Deploy the Lab

There's different variations of deploying SDDC's in VMC on AWS. You can deploy 30 instances in 15 orgs, deploy by org name, or deploy individually by SDDC name.  Examples below:

Usage:
`python3 manageworkshop.py --profile <profile name> --region <aws region> --cmd <create|delete|status|create-route|backup|restore|adduser|removeuser> --org <all|orgname(s)|sddcname(s)> --pwd <aws student password> --provider <AWS|ZEROCLOUD>`

- create for one org with 2 sddc's:
   `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd create --org vmc-ws1 --pwd VMware1!`
- create all 30 SDDC's in 15 orgs:
   `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd create --org all --pwd VMware1!`
- create one or more SDDC's by org name:
   `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd create --org vmc-ws1,vmcws2 --pwd VMware1!`
- create test deployment using ZEROCLOUD instance
   `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd create --org vmc-ws1 --pwd VMware1! --provider ZEROCLOUD`

## Status or State of the lab

When deploying or deleting the lab instances, you can get a status of the state of the AWS environment and VMC on AWS environment.

- Status of all SDDC's
  `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd status --org all`

## Adding or Removing Users

Add or remove users from the JSON configuration file.  Also have the ability to add/remove additional users outside of the configuration file.

- Add default users to all orgs
   `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd adduser --email all`
- Add external emails or users to an org
   `manageworkshop.py --profile vmcexpert1 --region us-west-2 --cmd adduser --org vmc-ws1 --email johndoe@vmware.com,janedoe@vmware.com`
- Remove default users to all orgs
   `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd removeuser --email all`

## List Users

List users and roles by organization.

- List users/role by org
  `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd listusers --org vmc-ws1`
- List all users/role
  `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd listusers --org all`

## Delete the labs

This removes all SDDC instances and AWS services deployed in AWS.

- Delete SDDC's from single org
  `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd delete --org vmc-ws1`
- Delete SDDC's individually
  `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd delete --org student1,student2`
- Delete all SDDC's in all orgs
  `manageWorkshop.py --profile vmcexpert1 --region us-west-2 --cmd delete --org all`


# Owner & Contributer:
Chris Lennon aka Crslen

Amaury Garde aka AmauryGarde

Thomas Sauerer aka xFirestyle2k


