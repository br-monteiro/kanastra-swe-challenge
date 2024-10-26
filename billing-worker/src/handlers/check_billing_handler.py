from src.handlers.abstract_handler import AbstractHandler
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage
from src.models.data_status import DataStatus
from src.cache.cache_client import CacheClient
from src.metrics.metrics_registry_manager import get_metrics_registry


METRICS = get_metrics_registry()
METRICS.register_counter("skipped_messages", "Skipped messages")


class CheckBillingHandler(AbstractHandler):
    def __init__(self, settings, cache_client: CacheClient):
        super().__init__(settings)
        self.cache_client = cache_client

    def handle(self, sqs_message: SQSMessage,  data_context: DataContext = None) -> DataContext:
        self.logger.debug('Check billing process', extra={
                          'sqs_message': sqs_message.content})

        if data_context.status == DataStatus.INVALID:
            self.logger.debug('Invalid context', extra={
                              'sqs_message': sqs_message.content})
            return super().handle(sqs_message,  data_context)

        cache_key = f"processed:{data_context.bill_details.debt_id}"
        if self.cache_client.get(cache_key):
            self.logger.debug('Bill already processed', extra={
                              'sqs_message': sqs_message.content})
            METRICS.get("skipped_messages").inc()
            data_context.status = DataStatus.SKIPPED

        return super().handle(sqs_message,  data_context)
