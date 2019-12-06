#!/usr/bin/env python
# Resource creation all working as intended

import boto3
import sys
import os
import sys

import time


# Usage
# Pass the number of VMs to start as a command-line argument
# The two necessary queues will be created
sqscli = boto3.client("sqs")
ec2 = boto3.resource("ec2")
ec2cli = boto3.client('ec2')
s3 = boto3.resource('s3')

try:
    created_queue_task = sqscli.create_queue(QueueName='task_queue', Attributes={'MessageRetentionPeriod': '180'})
    created_queue_end = sqscli.create_queue(QueueName='termination_queue', Attributes={'VisibilityTimeout': '0'})
except:
    print("Queues already exist")

num_vms_to_start = int(sys.argv[1])
vms = ec2.create_instances(
    ImageId='ami-00eb20669e0990cb4',
    MinCount=1,
    MaxCount=num_vms_to_start,
    InstanceType='t2.nano',
    SecurityGroupIds=[
        'sg-e73bcdb3',  # Allow incoming connections on port 22
        'sg-0deca82874684d70f'],  # default group
    KeyName='ec2-keypair'
)

sqscli = boto3.client('sqs')
task_queue_url = sqscli.get_queue_url(QueueName='task_queue')['QueueUrl']
print("Task queue url: ", task_queue_url)
termination_queue_url = sqscli.get_queue_url(QueueName='termination_queue')['QueueUrl']
print("Termination queue url: ", termination_queue_url)


# s3.create_bucket(Bucket='borsim.codebucket')
# s3.upload_file('awsnoncefinder.py', 'borsim.codebucket', 'awsnoncefinder.py')

# Associate policy to allow sqs access for ec2 instances
time.sleep(25)
for iid_dict in ec2cli.describe_instances(Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running']},
    ])['Reservations'][0]['Instances']:
    iid = iid_dict['InstanceId']
    try:
        response = ec2cli.associate_iam_instance_profile(
            IamInstanceProfile={
                'Arn': 'arn:aws:iam::516789663769:instance-profile/s3_sqs_full',
                'Name': 's3_sqs_full'
            },
            InstanceId=iid)
    except Exception as error:
        print(error, "Profile already associated")

for instance in ec2cli.describe_instances(Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running']},
    ])['Reservations'][0]['Instances']:
    hostname = instance['PublicDnsName']
    os.system('ssh-keyscan ' + hostname + ' >> ~/.ssh/known_hosts')
    os.system('scp -i ~/.ssh/ec2-keypair.pem awsnoncefinder.py ec2-user@' + hostname + ':~')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum install python36 -y')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum install python36-pip -y')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo pip-3.6 install boto3')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' python36 awsnoncefinder.py &')

