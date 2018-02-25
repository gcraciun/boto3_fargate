#!/usr/bin/env python

import boto3
import sys
import json
from botocore.exceptions import ClientError
import mycore


#project tags
ptags = {'Key': 'Project' , 'Value' : 'FargateTesting'}

vpc_data = {
    "vpc_CidrBlock" : "172.22.0.0/16",
    "vpc_Subnets": [ 
        { 
            "sub1_CidrBlock" : "172.22.1.0/24",
            "sub2_CidrBlock" : "172.22.2.0/24"
        }
    ]
}

try:
    inputf = sys.argv[1]
except:
    print "Error, no input file"
    exit(1)

def read_data(ifile):
    try:
        with open(ifile) as jsonfile:
            data = json.load(jsonfile)
            return data
    except:
        print "Error, could not open file"
        exit(1)

task_data = read_data(inputf)

#print task_data

# If it does not exist create Cloudwatch LogGroup.
# - Move from hardcoding to variable after testing.
cw = boto3.client('logs')
try:
    cw.create_log_group(
        logGroupName='Fargate-Test',
        tags = ptags,
        )
except ClientError as e:
    if e.response["Error"]["Code"] == 'ResourceAlreadyExistsException':
        print e.response["Error"]["Message"]
        print "Skpping log group creation..."
    else:
        print e
        exit(1)

try:
    ec2 = boto3.client('ec2')
except ClientError as e:
    print e
    exit(1)

fg_vpc = mycore.AWS_VPC(client=ec2, tag=ptags, CidrBlock=vpc_data["vpc_CidrBlock"])
fg_sub1 = mycore.AWS_VPC_SUBNET(client=ec2, tag=ptags, vpc_id=fg_vpc.id, CidrBlock=vpc_data["vpc_Subnets"][0]["sub1_CidrBlock"], AZ=fg_vpc.AZs)
fg_sub1 = mycore.AWS_VPC_SUBNET(client=ec2, tag=ptags, vpc_id=fg_vpc.id, CidrBlock=vpc_data["vpc_Subnets"][0]["sub2_CidrBlock"], AZ=fg_vpc.AZs)

# Get the ecs connection, create the cluster, don't forget "try"
ecs = boto3.client('ecs')
try:
    ecs.create_cluster(clusterName='GC-Test')
except ClientError as e:
    print e
    exit(1)
