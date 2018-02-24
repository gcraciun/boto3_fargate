#!/usr/bin/env python

import boto3
import sys
import json

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

print task_data

# If it does not exist create Cloudwatch LogGroup.
# - Move from hardcoding to variable after testing.
cw = boto3.client('logs')
try:
    loggroups = cw.describe_log_groups(logGroupNamePrefix='Fargate-Test')
#    loggroups = cw.describe_log_groups()
except:
    print "Error getting log groups"
    exit(1)

LGs = [ x["logGroupName"] for x in loggroups["logGroups"]]

lg_found = False # 2nd grade programming

if len(LGs) > 0:
    for temp in LGs:
        if temp == 'Fargate-Test':
            lg_found = True
            print "found existing log group with the same name"
            break

if not lg_found:
    print "proceeding with creation"
    try:
        newlg = cw.create_log_group(logGroupName='Fargate-Test')
    except:
        print "Error creating log group"
        exit(1)

print "\n\n\nExiting without running everything below"
exit(0)

# Get there first
try:
    ec2 = boto3.resource('ec2')
    vpc = ec2.create_vpc(CidrBlock='172.21.0.0/16')
except:
    print "Error creating VPC, send me to http://botocore.readthedocs.io/en/latest/client_upgrades.html#error-handling"
    exit(1)
print vpc.id


# Get available AZ's
try:
    ec2_cl = boto3.client('ec2')
    av_az = ec2_cl.describe_availability_zones()
    AZs = [x["ZoneName"] for x in av_az["AvailabilityZones"]]
except:
    print "Error getting AZ's"
    exit(1)

for x in AZs:
    print x
# ADD, I need to push in alphabetical order A, B, C, etc
AZs.reverse()


# Create subnet in 2 ways, so many choices...
# EC2.Client.create_subnet
# EC2.Vpc.create_subnet

try:
    print "Subnet 1 going"
    subnet1 = vpc.create_subnet(CidrBlock='172.21.1.0/24', AvailabilityZone=AZs.pop())
    print "Subnet 2 going"
    subnet2 = ec2.create_subnet(CidrBlock='172.21.2.0/24', VpcId=vpc.id, AvailabilityZone=AZs.pop())
except:
    print "Error creating subnets"
    exit(1)
print subnet1.id
print subnet2.id

# Get the ecs connection, create the cluster, don't forget "try"
ecs = boto3.client('ecs')
try:
    ecs.create_cluster(clusterName='GC-Test')
except:
    print "Error creating cluster"
