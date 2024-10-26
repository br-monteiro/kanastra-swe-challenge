from src.handlers.abstract_handler import AbstractHandler
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage
from src.models.data_status import DataStatus
from src.cache.cache_client import CacheClient
from src.metrics.metrics_registry_manager import get_metrics_registry


METRICS = get_metrics_registry()
METRICS.register_counter("billing_processed_successfully",
                         "Billing processed successfully")


class ProcessBillingHandler(AbstractHandler):
    def __init__(self, settings, cache_client: CacheClient):
        super().__init__(settings)
        self.cache_client = cache_client

    def handle(self, sqs_message: SQSMessage,  data_context: DataContext = None) -> DataContext:
        self.logger.debug('Process billing', extra={
                          'sqs_message': sqs_message.content})

        if data_context.status == DataStatus.INVALID:
            return super().handle(sqs_message,  data_context)

        if data_context.status == DataStatus.SKIPPED:
            return super().handle(sqs_message,  data_context)

        self.process(data_context)
        cache_key = f"processed:{data_context.bill_details.debt_id}"
        self.cache_client.set(
            cache_key, 1, self.settings.redis_data_expiration)

        data_context.status = DataStatus.PROCESSED

        return super().handle(sqs_message,  data_context)

    def process(self, data_context: DataContext) -> bool:
        """
        Do some magic here like processing the billing and others stuff
        """
        self.logger.debug('Processing billing', extra={
                          'debt_id': data_context.bill_details.debt_id})
        METRICS.get("billing_processed_successfully").inc()
        return True
