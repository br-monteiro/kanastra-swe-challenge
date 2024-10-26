from json import dumps
from src.handlers.abstract_handler import AbstractHandler
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage
from src.models.data_status import DataStatus
from src.cache.cache_client import CacheClient
from src.aws.sns.sns_client import SNSClient
from src.metrics.metrics_registry_manager import get_metrics_registry


METRICS = get_metrics_registry()
METRICS.register_counter("notification_sent", "Notification sent")


class NotificationHandler(AbstractHandler):
    def __init__(self, settings, cache_client: CacheClient, sns_client: SNSClient):
        super().__init__(settings)
        self.cache_client = cache_client
        self.sns_client = sns_client

    def handle(self, sqs_message: SQSMessage,  data_context: DataContext = None) -> DataContext:
        self.logger.debug('Notification', extra={
                          'sqs_message': sqs_message.content})

        if data_context.status == DataStatus.INVALID:
            return super().handle(sqs_message,  data_context)

        cache_key = f"notification:{data_context.bill_details.debt_id}"

        if not self.cache_client.get(cache_key):
            self.notify(data_context)
            self.cache_client.set(
                cache_key, 1, self.settings.redis_data_expiration)

        return super().handle(sqs_message,  data_context)

    def notify(self, data_context: DataContext) -> bool:
        """
        Send notification to the topic
        """
        self.logger.debug('Sending notification', extra={
                          'debt_id': data_context.bill_details.debt_id})

        json_data = dumps(data_context.bill_details.__dict__)
        self.sns_client.publish(json_data)
        METRICS.get("notification_sent").inc()
