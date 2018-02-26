#!/usr/bin/env python
import boto3
import json
from botocore.exceptions import ClientError

class AWS_VPC(object):
    def __init__(self, **kwargs):
        if kwargs is not None:
            self.ec2 = kwargs["client"]
            self.CidrBlock = kwargs["CidrBlock"]
            self.tag = kwargs["tag"]
        else:
            print "No client specified"
            exit(1)
        try:
            self.vpc = self.ec2.create_vpc(CidrBlock=self.CidrBlock)
        except ClientError as e:
            print e
            exit(1)
        self.id = self.vpc["Vpc"]["VpcId"]
        waiter = self.ec2.get_waiter('vpc_available')
        waiter.wait(VpcIds=[self.id])
        self.__tag(self.tag)
        self.__getAZ()

    def __tag(self, tag):
        try:
            self.tag_r = self.ec2.create_tags(
                Resources=[self.id],
                Tags=self.tag)
        except ClientError as e:
            print e
            exit(1)

    def __getAZ(self):
        try:
            av_az = self.ec2.describe_availability_zones()
        except ClientError as e:
            print e
            exit(1)
        self.AZs = [x["ZoneName"] for x in av_az["AvailabilityZones"]]
        self.AZs.reverse()


class AWS_VPC_SUBNET(object):
    def __init__(self, **kwargs):
        if kwargs is not None:
            self.vpc_id = kwargs["vpc_id"]
            self.CidrBlock = kwargs["CidrBlock"]
            self.AZ = kwargs["AZ"].pop()
            self.ec2 = kwargs["client"]
            self.tag = kwargs["tag"]
            try:
                self.response = self.ec2.create_subnet(CidrBlock=self.CidrBlock, VpcId=self.vpc_id, AvailabilityZone=self.AZ)
            except ClientError as e:
                print e
                exit(1)
            self.id = self.response["Subnet"]["SubnetId"]
            waiter = self.ec2.get_waiter('subnet_available')
            waiter.wait(SubnetIds=[self.id])
            self.__tag(self.tag)
            self.__map_pub()
                
    def __tag(self, tag):
        try:
            self.tag_r = self.ec2.create_tags(
                Resources=[self.id],
                Tags=self.tag)
        except ClientError as e:
            print e
            exit(1)
            
    def __map_pub(self):
        try:
            response = self.ec2.modify_subnet_attribute(
                MapPublicIpOnLaunch={'Value': True},
                SubnetId=self.id)
        except ClientError as e:
            print e
            exit(1)

class AWS_CWL(object):
    def __init__(self, **kwargs):
        if kwargs is not None:
            self.cw = kwargs["client"]
            self.tag = kwargs["tag"]
            self.name = kwargs["name"]
            try:
                self.cw.create_log_group(logGroupName=self.name, tags=self.tag)
            except ClientError as e:
                if e.response["Error"]["Code"] == 'ResourceAlreadyExistsException':
                    print e.response["Error"]["Message"]
                    print "Skpping log group creation..."
                else:
                    print e
                    exit(1)
    
class AWS_ECS(object):
    def __init__(self, **kwargs):
        if kwargs is not None:
            self.ecs = kwargs["client"]
            self.name = kwargs["name"]
            try:
                response = self.ecs.create_cluster(clusterName=self.name)
            except ClientError as e:
                print e
                exit(1)
            self.arn = response["cluster"]["clusterArn"]
            
class AWS_ECS_TSK_DEF(object):
    def __init__(self, **kwargs):
        if kwargs is not None:
            self.ecs = kwargs["client"]
            self.data = kwargs["data"]
            try:
                response = self.ecs.register_task_definition(family = self.data["family"],
                                                                taskRoleArn = self.data["taskRoleArn"],
                                                                executionRoleArn = self.data["executionRoleArn"],
                                                                networkMode = self.data["networkMode"],
                                                                containerDefinitions = self.data["containerDefinitions"],
                                                                cpu = self.data["cpu"],
                                                                memory = self.data["memory"],
                                                                requiresCompatibilities = self.data["requiresCompatibilities"])
            except ClientError as e:
                print e
                exit(1)
            self.arn = response["taskDefinition"]["taskDefinitionArn"]

class AWS_ECS_TSK_RUN(object):
    def __init__(self, **kwargs):
        if kwargs is not None:
            self.ecs = kwargs["client"]
            self.cluster = kwargs["cluster"]
            self.taskDefinition = kwargs["taskDefinition"]
            self.count = kwargs["count"]
            self.launchType = kwargs["launchType"]
            self.networkConfiguration = kwargs["networkConfiguration"]
            try:
                response = self.ecs.run_task(cluster = self.cluster,
                                                taskDefinition = self.taskDefinition,
                                                count = self.count,
                                                launchType = self.launchType,
                                                networkConfiguration = self.networkConfiguration)
            except ClientError as e:
                print e
                exit(1)
            self.arn = response["tasks"][0]["taskArn"]

def read_data(ifile):
    try:
        with open(ifile) as jsonfile:
            data = json.load(jsonfile)
            return data
    except:
        print "Error, could not open file"
        exit(1)


if __name__ == '__main__':

    print "Do not run me"
    exit(1)

"""
    ptags = {'Key': 'Project' , 'Value' : 'FargateTesting'}
    vpc_cidr='172.22.0.0/16'

    ec2 = boto3.client('ec2')
    my_vpc = AWS_VPC(client=ec2, tag=ptags, CidrBlock=vpc_cidr)
    print my_vpc.id
    print my_vpc.AZs

    subnet1_cidr='172.22.1.0/24'
    subnet2_cidr='172.22.2.0/24'
    my_subnet1 = AWS_VPC_SUBNET(client=ec2, tag=ptags, vpc_id=my_vpc.id, CidrBlock=subnet1_cidr, AZ=my_vpc.AZs)
    my_subnet2 = AWS_VPC_SUBNET(client=ec2, tag=ptags, vpc_id=my_vpc.id, CidrBlock=subnet2_cidr, AZ=my_vpc.AZs)
"""
