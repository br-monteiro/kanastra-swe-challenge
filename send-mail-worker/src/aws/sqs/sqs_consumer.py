import boto3
from src.aws.sqs.exceptions.sqs_consumer_exception import SQSConsumerException
from src.config.settings import Settings
from src.logger.logger import get_logger
from src.models.sqs_message import SQSMessage
from src.metrics.metrics_registry_manager import get_metrics_registry


METRICS = get_metrics_registry()
METRICS.register_counter("sqs_consumer_messages_received",
                         "Number of messages received by the SQS consumer")
METRICS.register_counter("sqs_consumer_messages_deleted",
                         "Number of messages deleted by the SQS consumer")


class SQSConsumer:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None
        self.logger = get_logger(__name__)

    def create_client(self):
        self._client = boto3.client(
            "sqs",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.sqs_endpoint_url
        )
        self.logger.info("Client created")

    def consume(self, run_forever=True):
        self._validate_client()
        should_run_forever = True
        while should_run_forever:
            should_run_forever = run_forever
            messages = self._get_messages()
            for message in messages:
                METRICS.get("sqs_consumer_messages_received").inc()
                yield SQSMessage(message)

    def delete_message(self, message: SQSMessage):
        self._validate_client()
        queue_url = self.settings.sqs_queue_url
        try:
            self._client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message.receipt_handle
            )
            self.logger.debug("Message deleted", extra={
                              "_message": message.content})
            METRICS.get("sqs_consumer_messages_deleted").inc()
        except Exception as e:
            self.logger.error("Error deleting message", extra={"error": e})

    def _get_messages(self):
        queue_url = self.settings.sqs_queue_url
        messages = self._client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=self.settings.sqs_max_messages,
            WaitTimeSeconds=self.settings.sqs_wait_time_seconds
        )
        return messages.get("Messages", [])

    def _validate_client(self):
        if not self._client:
            message = "SQS client not created"
            self.logger.error(message)
            raise SQSConsumerException(message)
