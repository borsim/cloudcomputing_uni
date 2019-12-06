#!/usr/bin/env python
# Working as intended.
# Also accepts the 4 parameters as command-line arguments in the asked order
# Extension possibility: add "not found" termination
# Extension possibility: add jobIDs
# Extension possibility: warn user when # of VMs required are not available

import time
import random
import boto3
import sys

sqscli = boto3.client("sqs")
task_queue_url = sqscli.get_queue_url(QueueName='task_queue')['QueueUrl']
termination_queue_url = sqscli.get_queue_url(QueueName='termination_queue')['QueueUrl']


def create_task(from_num, to_num, difficulty_bits, message):
    response = sqscli.send_message(
        QueueUrl=task_queue_url,
        DelaySeconds=0,
        MessageAttributes={
            'minnonce': {
                'DataType': 'String',
                'StringValue': str(from_num)
            },
            'maxnonce': {
                'DataType': 'String',
                'StringValue': str(to_num)
            },
            'difficulty_bits': {
                'DataType': 'String',
                'StringValue': str(difficulty_bits)
            },
            'secret_message': {
                'DataType': 'String',
                'StringValue': message
            }
        },
        MessageBody='Task given to VM to find golden nonce')


def await_termination():
    nonce_found = False
    termination_msg = {}
    while not nonce_found:
        response = sqscli.receive_message(QueueUrl=termination_queue_url,
                                       AttributeNames=['SentTimestamp'],
                                       MessageAttributeNames=['All'])
        try:
            termination_msg = response['Messages'][0]
            nonce_found = True
        except:
            pass
    if termination_msg['MessageAttributes']['termination']['StringValue'] != "":
        return termination_msg


def parse_termination_message(termination_msg):
    receipt_handle = termination_msg['ReceiptHandle']
    noncevalue = int(termination_msg['MessageAttributes']['nonce_value']['StringValue'])
    noncehash = termination_msg['MessageAttributes']['nonce_hash']['StringValue']

    before_delay = time.time()

    return noncevalue, noncehash, before_delay, receipt_handle


if __name__ == "__main__":
    startTime = time.time()
    if len(sys.argv) - 1 == 4:
        diff_b = int(sys.argv[1])
        sec_m = sys.argv[2]
        num_m = int(sys.argv[3])
        prob = float(sys.argv[4])
    else:
        diff_b = input("Please enter the difficulty bits for the nonce (default: 23): ")
        if diff_b == '':
            diff_b = 23
        else:
            diff_b = int(diff_b)
        sec_m = input("Please enter the secret for the nonce (default: deadbeef1234): ")
        if sec_m == '':
            sec_m = 'deadbeef1234'
        num_m = input("Please enter the number of VMs requisitoned (default: 1): ")
        if num_m == '':
            num_m = 1
        else:
            num_m = int(num_m)
        prob = input("Please enter the safety margin - "+
                     "how many times above the expected value should nonces be checked (default: 2): ")
        if prob == '':
            prob = 2
        else:
            prob = float(prob)
        if prob <= 0:
            prob = 2
    num_expected_hashes = 2 ** diff_b
    hash_per_sec_benchmark = 374381
    queue_overhead = 16
    expected_time = num_expected_hashes / hash_per_sec_benchmark
    print("Expected time (without queue overhead): ", expected_time, " seconds")
    print("Expected time (with queue overhead): ", expected_time + queue_overhead, " seconds")
    for i in range(0, num_m):
        create_task(i * (num_expected_hashes * prob), (i+1) * (num_expected_hashes * prob), diff_b, sec_m)
    msg = await_termination()
    nv, nh, endTime, rec_h = parse_termination_message(msg)
    print("Nonce found: ", nv)
    print("Hash value: ", nh)
    print("Time taken: ", (endTime - startTime), " seconds")
    print("Leaving 12 seconds for task termination on queue...")
    time.sleep(12)  # Leave time for VMs to read termination message
    # Empty queue for cleanup
    sqscli.delete_message(
        QueueUrl=termination_queue_url,
        ReceiptHandle=rec_h
    )

