import boto3
from src.config.settings import Settings
from src.logger.logger import get_logger
from src.aws.sqs.exceptions.sqs_client_exception import SQSClientException


class SQSClient:
    def __init__(self, settings: Settings):
        self._client = None
        self.settings = settings
        self.logger = get_logger(__name__)

    def create_client(self):
        self._client = boto3.client(
            "sqs",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.sqs_endpoint_url
        )
        self.logger.info("SQS client created")

    def send_message(self, queue_url: str, message_body: str):
        self._validate_client()
        self._client.send_message(QueueUrl=queue_url, MessageBody=message_body)
        self.logger.debug(
            f"Message sent to queue {queue_url}",
            extra={
                "message_body": message_body
            }
        )

    def _validate_client(self):
        if not self._client:
            message = "SQS client not created"
            self.logger.error(message)
            raise SQSClientException(message)
