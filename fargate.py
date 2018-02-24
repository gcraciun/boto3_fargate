#!/usr/bin/env python

import boto3
import sys
import json
from botocore.exceptions import ClientError

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
    cw.create_log_group(logGroupName='Fargate-Test')
except ClientError as e:
    if e.response["Error"]["Code"] == 'ResourceAlreadyExistsException':
        print e.response["Error"]["Message"]
        print "Skpping log group creation..."
    else:
        print e
        exit(1)

try:
    ec2 = boto3.client('ec2')
    vpc = ec2.create_vpc(CidrBlock='172.21.0.0/16')
except ClientError as e:
    print e
    exit(1)

vpc_id = vpc["Vpc"]["VpcId"]
print vpc_id


# Get available AZ's
try:
    av_az = ec2.describe_availability_zones()
except ClientError as e:
    print e
    exit(1)

AZs = [x["ZoneName"] for x in av_az["AvailabilityZones"]]
for x in AZs:
    print x
AZs.reverse() # ADD, I need to push in alphabetical order A, B, C, etc

try:
    print "Subnet 1 going"
    subnet1 = ec2.create_subnet(CidrBlock='172.21.1.0/24', VpcId=vpc_id, AvailabilityZone=AZs.pop())
    print "Subnet 2 going"
    subnet2 = ec2.create_subnet(CidrBlock='172.21.2.0/24', VpcId=vpc_id, AvailabilityZone=AZs.pop())
except ClientError as e:
    print e
    exit(1)

print subnet1["Subnet"]["SubnetId"]
print subnet2["Subnet"]["SubnetId"]

# Get the ecs connection, create the cluster, don't forget "try"
ecs = boto3.client('ecs')
try:
    ecs.create_cluster(clusterName='GC-Test')
except ClientError as e:
    print e
    exit(1)
