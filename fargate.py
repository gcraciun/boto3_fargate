#!/usr/bin/env python

import boto3

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
ecs.create_cluster(clusterName='GC-Test')
