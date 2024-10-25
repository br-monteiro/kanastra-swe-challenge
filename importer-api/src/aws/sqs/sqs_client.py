import boto3
from src.config.settings import Settings
from src.logger.logger import get_logger
from src.aws.sqs.exceptions.sqs_client_exception import SQSClientException


class SQSClient:
    def __init__(self, queue_url: str, settings: Settings):
        self._client = None
        self.queue_url = queue_url
        self.settings = settings
        self.logger = get_logger(__name__)

    def create_client(self):
        self._client = boto3.client(
            "sqs",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.sqs_endpoint_url
        )
        self.logger.info("SQS client created")

    def send_message(self, message_body: str):
        self._validate_client()

        try:
            self._client.send_message(
                QueueUrl=self.queue_url, MessageBody=message_body)
            self.logger.debug(
                f"Message sent to queue {self.queue_url}",
                extra={
                    "message_body": message_body
                }
            )
        except Exception as e:
            self.logger.error(
                f"Error sending message to queue {self.queue_url}",
                extra={
                    "message_body": message_body,
                    "error": str(e)
                }
            )

    def send_message_batch(self, messages: list):
        self._validate_client()

        entries = [
            {"Id": str(i), "MessageBody": message} for i, message in enumerate(messages)
        ]

        try:
            self._client.send_message_batch(
                QueueUrl=self.queue_url,
                Entries=entries
            )
            self.logger.debug(
                f"Messages sent to queue {self.queue_url}",
                extra={
                    "messages": messages
                }
            )
        except Exception as e:
            self.logger.error(
                f"Error sending messages to queue {self.queue_url}",
                extra={
                    "messages": messages,
                    "error": str(e)
                }
            )

    def _validate_client(self):
        if not self._client:
            message = "SQS client not created"
            self.logger.error(message)
            raise SQSClientException(message)
