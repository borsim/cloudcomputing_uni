#!/usr/bin/env python
# Everything working as intended in this one. Hooray.

import boto3
import time

sqscli = boto3.client('sqs')
termination_queue_url = sqscli.get_queue_url(QueueName='termination_queue')['QueueUrl']


def send_nonce_found_message(nonce_value, nonce_hash):
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
            }
        },
        MessageBody='Nonce found. Other VMs can stop working')


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
    if termination_msg['MessageAttributes']['termination'] != "":
        return termination_msg


def delete_message(termination_msg):
    receipt_handle = termination_msg['ReceiptHandle']

    print("Leaving 15 seconds for task termination on queue...")
    time.sleep(15)  # Leave time for VMs to read termination message
    sqscli.delete_message(
        QueueUrl=termination_queue_url,
        ReceiptHandle=receipt_handle
    )
    print("Tasks terminated, message deleted.")


if __name__ == "__main__":
    send_nonce_found_message(-1, "tasks terminated")
    print("Termination message sent.")
    msg = await_termination()
    delete_message(msg)
