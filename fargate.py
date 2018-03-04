#!/usr/bin/env python

import boto3
import sys
import json
from botocore.exceptions import ClientError
import mycore

# Data about the resources to be created, stored in JSON format
# including resource tags
vpc_data = {
    "vpc_CidrBlock" : "172.22.0.0/16",
    "vpc_Subnets" : [ 
        { 
            "sub1_CidrBlock" : "172.22.1.0/24",
            "sub2_CidrBlock" : "172.22.2.0/24"
        }
    ],
    "ptags" : [
        {
            "Key" : "Project",
            "Value" : "FargateTesting"
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

# Create Cloudwatch logs
fg_cwl = mycore.AWS_CWL(client=cw, tag=vpc_data["ptags"][0], name=vpc_data["cwl_name"])

# Create the VPC to which the container will be attached
fg_vpc = mycore.AWS_VPC(client=ec2, tag=vpc_data["ptags"], CidrBlock=vpc_data["vpc_CidrBlock"])

# Create a route table inside the VPC (don't use the main RT)
fg_rtab = mycore.AWS_VPC_RTAB(client=ec2, tag=vpc_data["ptags"], vpc_id=fg_vpc.id)

# Create 2 subnets and associate them to the previous route table
fg_sub1 = mycore.AWS_VPC_SUBNET(client=ec2, tag=vpc_data["ptags"], vpc_id=fg_vpc.id, CidrBlock=vpc_data["vpc_Subnets"][0]["sub1_CidrBlock"], AZ=fg_vpc.AZs)
fg_sub2 = mycore.AWS_VPC_SUBNET(client=ec2, tag=vpc_data["ptags"], vpc_id=fg_vpc.id, CidrBlock=vpc_data["vpc_Subnets"][0]["sub2_CidrBlock"], AZ=fg_vpc.AZs)
fg_sub1rta = mycore.AWS_VPC_RTASSOC(client=ec2, rtid=fg_rtab.id, subid=fg_sub1.id)
fg_sub2rta = mycore.AWS_VPC_RTASSOC(client=ec2, rtid=fg_rtab.id, subid=fg_sub2.id)

# Create an Internet Gateway
fg_igw = mycore.AWS_VPC_IGW(client=ec2, tag=vpc_data["ptags"], vpc_id=fg_vpc.id)

# Route all traffic in the route table towards the Internet Gateway
fg_route = mycore.AWS_VPC_RTCRT(client=ec2, dst_cidr="0.0.0.0/0", rtid=fg_rtab.id, igw_id=fg_igw.id)

# Create ECS cluster
fg_ecs = mycore.AWS_ECS(client=ecs, name=vpc_data["ecs_name"])

# Create task definition (task data is read from a file, first parameter, json format)
fg_tsk_def = mycore.AWS_ECS_TSK_DEF(client=ecs, data=task_data)

# Create temporary information needed for running the task
netconfig_dict = {
                    "awsvpcConfiguration" : {
                        "subnets" : [ fg_sub1.id, fg_sub2.id],
                        "assignPublicIp" : "ENABLED"
                    }
}

# Finally run the task
fg_tsk_run = mycore.AWS_ECS_TSK_RUN(client=ecs,
                                        cluster=fg_ecs.arn,
                                        taskDefinition=fg_tsk_def.arn,
                                        count=1,
                                        launchType="FARGATE",
                                        networkConfiguration=netconfig_dict)
