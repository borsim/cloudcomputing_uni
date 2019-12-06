#!/usr/bin/env python

import time
import hashlib
import boto3

# Working as intended.


intmax = 2 ** 32 - 1
secretmessage = "deadbeef"
minnonce = 0
maxnonce = intmax
difficulty_bits = 23

sqscli = boto3.client('sqs', region_name='us-east-1')
task_queue_url = sqscli.get_queue_url(QueueName='task_queue')['QueueUrl']
termination_queue_url = sqscli.get_queue_url(QueueName='termination_queue')['QueueUrl']


def read_task_message():
    has_task = False
    while not has_task:
        time.sleep(.200)
        response = sqscli.receive_message(QueueUrl=task_queue_url,
                                          AttributeNames=['SentTimestamp'],
                                          MessageAttributeNames=['All'])
        try:
            taskmsg = response['Messages'][0]
            has_task = True
            print("Task received, beginning work.")
        except Exception as error:
            print("No task in queue.")
    return taskmsg


def parse_task_message(task_msg):
    receipt_handle = task_msg['ReceiptHandle']
    _minnonce = int(task_msg['MessageAttributes']['minnonce']['StringValue'])
    _maxnonce = int(task_msg['MessageAttributes']['maxnonce']['StringValue'])
    _difficulty_bits = int(task_msg['MessageAttributes']['difficulty_bits']['StringValue'])
    _secret_message = task_msg['MessageAttributes']['secret_message']['StringValue']
    _jobid = task_msg['MessageAttributes']['jobid']['StringValue']

    sqscli.delete_message(
        QueueUrl=task_queue_url,
        ReceiptHandle=receipt_handle
    )
    return _minnonce, _maxnonce, _difficulty_bits, _secret_message, _jobid


def read_termination_messages(uid):
    response = sqscli.receive_message(QueueUrl=termination_queue_url,
                                      AttributeNames=['SentTimestamp'],
                                      MessageAttributeNames=['All'])
    try:
        terminationmsg = response['Messages'][0]
        if terminationmsg['MessageAttributes']['termination']['StringValue'] == "Nonce found" and uid == terminationmsg['MessageAttributes']['jobid']['StringValue']:
            return True
    except Exception as error:
        pass
    return False


def send_nonce_found_message(nonce_value, nonce_hash, uid):
    response = sqscli.send_message(
        QueueUrl=termination_queue_url,
        DelaySeconds=0,
        MessageAttributes={
            'termination': {
                'DataType': 'String',
                'StringValue': 'Nonce found'
            },
            'nonce_value': {
                'DataType': 'String',
                'StringValue': str(nonce_value)
            },
            'nonce_hash': {
                'DataType': 'String',
                'StringValue': nonce_hash
            },
            'jobid': {
                'DataType': 'String',
                'StringValue': uid
            }
        },
        MessageBody='Nonce found. Other VMs can stop working')


def find_golden_nonce(uid):
    target = 2 ** (256 - difficulty_bits)
    termination_check_interval = 2 ** difficulty_bits / 8
    nonce = minnonce
    while nonce < maxnonce:
        if nonce % termination_check_interval == 0:
            print("Current nonce attempt: ", nonce)
            if read_termination_messages(uid):
                return -1
        to_hash = (str(secretmessage) + str(nonce)).encode("utf-8")
        nonce_hashed = hashlib.sha256(to_hash).hexdigest()
        if int(nonce_hashed, 16) < target:
            print("Nonce found: ", nonce)
            print("Hash value: ", nonce_hashed)
            send_nonce_found_message(nonce, nonce_hashed, uid)
            return nonce
        nonce += 1
    print("Nonce not found within boundary, stopping work")
    return -1


if __name__ == "__main__":
    while True:
        task = read_task_message()
        minnonce, maxnonce, difficulty_bits, secretmessage, jobid = parse_task_message(task)
        print(minnonce, maxnonce, difficulty_bits, secretmessage, jobid)

        start_time = time.time()
        found_nonce = find_golden_nonce(jobid)
        end_time = time.time()

        time_taken = end_time - start_time
        print("Elapsed time: ", time_taken, " seconds")