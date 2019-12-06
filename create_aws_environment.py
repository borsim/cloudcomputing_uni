#!/usr/bin/env python
# Resource creation all working as intended

import boto3
import sys
import os
import sys
import multiprocessing
#from joblib import Parallel, delayed
from pssh.clients.native import ParallelSSHClient
import time
from subprocess import Popen


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


# def setup_instance(instance):
#     instance.load()
#     iid = ec2cli.describe_instances(instance)['InstanceIds'][0]
#     response = ec2cli.associate_iam_instance_profile(
#         IamInstanceProfile={
#             'Arn': 'arn:aws:iam::516789663769:instance-profile/s3_sqs_full',
#             'Name': 's3_sqs_full'
#         },
#         InstanceId=iid
#     )
#     hostname = str(instance.public_dns_name) + '\n'
#     os.system('ssh-keyscan '+ hostname + ' >> ~/.ssh/known_hosts')
#     os.system('scp -i ~/.ssh/ec2-keypair.pem awsnoncefinder.py ec2-user@' + hostname + ':~')
#     os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum update -y')
#     os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum install python36 -y')
#     os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum install python36-pip -y')
#     os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo pip-3.6 install boto3 -y')
#     os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' python awsnoncefinder.py')


# s3.create_bucket(Bucket='borsim.codebucket')
# s3.upload_file('awsnoncefinder.py', 'borsim.codebucket', 'awsnoncefinder.py')

# hostfile = open("pssh_hosts.txt", "w")
# Associate policy to allow sqs access for ec2 instances
time.sleep(15)
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
# Parallel(n_jobs=multiprocessing.cpu_count())(delayed(print("Instance set up"))(setup_instance(inst)) for inst in ec2.instances.all())

hosts = []
for instance in ec2cli.describe_instances(Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running']},
    ])['Reservations'][0]['Instances']:
    hostname = instance['PublicDnsName']
    hosts.append(hostname)
    os.system('ssh-keyscan ' + hostname + ' >> ~/.ssh/known_hosts')
    os.system('scp -i ~/.ssh/ec2-keypair.pem awsnoncefinder.py ec2-user@' + hostname + ':~')
    # os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum update -y')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum install python36 -y')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo yum install python36-pip -y')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' sudo pip-3.6 install boto3')
    os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' python36 awsnoncefinder.py &')
    # proc = Popen('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' python36 awsnoncefinder.py',
    #             shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    # os.system('ssh -i ~/.ssh/ec2-keypair.pem ec2-user@' + hostname + ' python36 awsnoncefinder.py')
# client = ParallelSSHClient(hosts)
# output = client.run_command('sudo yum update -y')
# output = client.run_command('sudo yum install python36 -y')
# output = client.run_command('sudo yum install python36-pip -y')
# output = client.run_command('sudo pip-3.6 install boto3 -y')
# output = client.run_command('python awsnoncefinder.py')


#    hostfile.write(hostname)
# hostfile.close()
# os.system('echo yes | pssh -h pssh_hosts.txt s3cmd get s3://code_bucket/awsnoncefinder.py awsnoncefinder.py')
# s3.download_file('code_bucket', 'awsnoncefinder.py', 'awsnoncefinder.py')
# os.system('s3cmd get s3://code_bucket/awsnoncefinder.py awsnoncefinder.py')
# os.system('scp awsnoncefinder.py awsnoncefinder.py')
# os.system('pssh -h pssh_hosts.txt python3 awsnoncefinder.py')
# echo yes | scp -i ~/.ssh/ec2-keypair.pem awsnoncefinder.py  ec2-user@ec2-52-91-96-49.compute-1.amazonaws.com:~
