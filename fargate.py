#!/usr/bin/env python

import boto3
import sys
import json
from botocore.exceptions import ClientError
import mycore

# Project resources tags
ptags = {'Key': 'Project' , 'Value' : 'FargateTesting'}

# Data about the resources to be created, stored in JSON format
vpc_data = {
    "vpc_CidrBlock" : "172.22.0.0/16",
    "vpc_Subnets": [ 
        { 
            "sub1_CidrBlock" : "172.22.1.0/24",
            "sub2_CidrBlock" : "172.22.2.0/24"
        }
    ],
    "cwl_name" : "Fargate-Test",
    "ecs_name" : "Fargate-Test"
}

# Read JSON file containing the Fargate Task data
try:
    inputf = sys.argv[1]
except:
    print "Error, no input file"
    exit(1)

task_data = mycore.read_data(inputf)


# Create Boto3 clients
try:
    cw = boto3.client('logs')
    ec2 = boto3.client('ec2')
    ecs = boto3.client('ecs')
except ClientError as e:
    print e
    exit(1)

# Create the necessary resources
fg_cwl = mycore.AWS_CWL(client=cw, tag=ptags, name=vpc_data["cwl_name"])
fg_vpc = mycore.AWS_VPC(client=ec2, tag=ptags, CidrBlock=vpc_data["vpc_CidrBlock"])
fg_sub1 = mycore.AWS_VPC_SUBNET(client=ec2, tag=ptags, vpc_id=fg_vpc.id, CidrBlock=vpc_data["vpc_Subnets"][0]["sub1_CidrBlock"], AZ=fg_vpc.AZs)
fg_sub1 = mycore.AWS_VPC_SUBNET(client=ec2, tag=ptags, vpc_id=fg_vpc.id, CidrBlock=vpc_data["vpc_Subnets"][0]["sub2_CidrBlock"], AZ=fg_vpc.AZs)
fg_ecs = mycore.AWS_ECS(client=ecs, name=vpc_data["ecs_name"])
