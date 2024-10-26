#!/bin/bash

apt install jq -y

echo "Creating SQS queues"
awslocal sqs create-queue --queue-name data-process
awslocal sqs create-queue --queue-name data-process-dlq
awslocal sqs create-queue --queue-name process-email


echo "Creating SNS topic"
awslocal sns create-topic --name data-process-topic


data_process_queue_url=$(awslocal sqs get-queue-url --queue-name data-process | jq -r '.QueueUrl')
data_process_dlq_arn=$(awslocal sqs get-queue-attributes --queue-url $data_process_queue_url --attribute-names QueueArn | jq -r '.Attributes.QueueArn')
data_process_topic_arn=$(awslocal sns list-topics | jq -r '.Topics[] | select(.TopicArn | contains("data-process-topic")).TopicArn')


echo "Config queue data-process"
awslocal sqs set-queue-attributes --queue-url $data_process_queue_url --attributes '{"RedrivePolicy": "{\"deadLetterTargetArn\":\"$data_process_dlq_arn\",\"maxReceiveCount\":\"5\"}"}'


echo "Subscribe process-email to data-process-topic"
process_email_queue_url=$(awslocal sqs get-queue-url --queue-name process-email | jq -r '.QueueUrl')
process_email_arn=$(awslocal sqs get-queue-attributes --queue-url $process_email_queue_url --attribute-names QueueArn | jq -r '.Attributes.QueueArn')
awslocal sns subscribe --topic-arn $data_process_topic_arn --protocol sqs --notification-endpoint $process_email_arn


echo "finish"
