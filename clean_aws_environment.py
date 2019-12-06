#!/usr/bin/env python
# Working as intended.

import boto3

ec2 = boto3.resource('ec2')
sqscli = boto3.client('sqs', region_name='us-east-1')
s3 = boto3.resource('s3')

# Terminate ec2 instances
try:
    for instance in ec2.instances.all():
        response = instance.terminate()
except Exception as error:
    print(error, "No ec2 instances running, cannot terminate.")

# Delete sqs queues
try:
    task_queue_url = sqscli.get_queue_url(QueueName='task_queue')['QueueUrl']
    termination_queue_url = sqscli.get_queue_url(QueueName='termination_queue')['QueueUrl']
    response1 = sqscli.delete_queue(QueueUrl=task_queue_url)
    response2 = sqscli.delete_queue(QueueUrl=termination_queue_url)
except Exception as error:
    print(error, "Queue resources to delete don't exist.")

# Delete code bucket
# try:
#     for bucket in s3.buckets.all():
#         for key in bucket.objects.all():
#             try:
#                 response = key.delete()
#             except Exception as error:
#                 print(error)
#     bucket.delete()
# except Exception as error:
#     print(error, " No bucket to delete")
