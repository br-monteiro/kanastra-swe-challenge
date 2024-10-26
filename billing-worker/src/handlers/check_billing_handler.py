from src.handlers.abstract_handler import AbstractHandler
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage
from src.models.data_status import DataStatus
from src.cache.cache_client import CacheClient


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

        if data_context.bill_details.has_been_processed:
            self.logger.debug('Bill already processed', extra={
                              'sqs_message': sqs_message.content})
            data_context.status = DataStatus.SKIPPED
            return super().handle(sqs_message,  data_context)

        if self.cache_client.get(data_context.bill_details.debt_id):
            self.logger.debug('Bill already processed', extra={
                              'sqs_message': sqs_message.content})
            data_context.status = DataStatus.SKIPPED

        return super().handle(sqs_message,  data_context)
