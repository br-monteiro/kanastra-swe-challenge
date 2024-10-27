from json import dumps
from src.config.settings import Settings
from src.handlers.abstract_handler import AbstractHandler
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage
from src.models.data_status import DataStatus
from src.cache.cache_client import CacheClient
from src.services.notification_service import NotificationService


class NotificationScheduleHandler(AbstractHandler):
    def __init__(self, settings: Settings, cache_client: CacheClient, notification_service: NotificationService):
        super().__init__(settings)
        self.cache_client = cache_client
        self.notification_service = notification_service

    def handle(self, sqs_message: SQSMessage,  data_context: DataContext = None) -> DataContext:
        self.logger.debug('Notification', extra={
                          'sqs_message': sqs_message.content})

        if data_context.status == DataStatus.INVALID:
            return super().handle(sqs_message,  data_context)

        cache_key = f"notification:{data_context.bill_details.debt_id}"

        if not self.cache_client.get(cache_key):
            self.schedule(data_context)
            self.cache_client.set(
                cache_key, 1, self.settings.redis_data_expiration)

        return super().handle(sqs_message, data_context)

    def schedule(self, data_context: DataContext) -> bool:
        self.logger.debug('Schedule notification', extra={
                          'debt_id': data_context.bill_details.debt_id})
        json_data = dumps(data_context.bill_details.__dict__)
        self.notification_service.enqueue(json_data).flush()
