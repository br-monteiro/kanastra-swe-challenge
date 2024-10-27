import boto3
from src.config.settings import Settings
from src.logger.logger import get_logger
from src.aws.sns.exceptions.sns_client_exception import SNSClientException
from src.metrics.metrics_registry_manager import get_metrics_registry


METRICS = get_metrics_registry()
METRICS.register_counter("notification_sent", "Notification sent")
METRICS.register_counter("notification_sent_errors", "Notification sent with errors")


class SNSClient:
    def __init__(self, topic_arn: str, settings: Settings):
        self._client = None
        self.topic_arn = topic_arn
        self.settings = settings
        self.logger = get_logger(__name__)

    def create_client(self):
        self._client = boto3.client(
            "sns",
            region_name=self.settings.aws_region,
            endpoint_url=self.settings.sns_endpoint_url
        )
        self.logger.debug("SNS client created")

    def publish(self, message: str):
        self._validate_client()
        self._client.publish(
            TopicArn=self.topic_arn,
            Message=message
        )
        self.logger.debug(f"Message published to topic {
                          self.topic_arn}", extra={"content": message})
        METRICS.get("notification_sent").inc()

    def publish_batch(self, messages: list):
        self._validate_client()

        messages_len = len(messages)

        entries = [
            {"Id": str(i), "Message": message} for i, message in enumerate(messages)
        ]

        try:
            self._client.publish_batch(
                TopicArn=self.topic_arn,
                PublishBatchRequestEntries=entries
            )
            self.logger.debug(
                f"Messages published to topic {self.topic_arn}",
                extra={
                    "messages": messages
                }
            )
            METRICS.get("notification_sent").inc(messages_len)
        except Exception as e:
            self.logger.error(
                f"Error publishing messages to topic {self.topic_arn}",
                extra={
                    "messages": messages,
                    "error": str(e)
                }
            )
            METRICS.get("notification_sent_errors").inc(messages_len)

    def _validate_client(self):
        if not self._client:
            message = "SNS client not created"
            self.logger.error(message)
            raise SNSClientException(message)
