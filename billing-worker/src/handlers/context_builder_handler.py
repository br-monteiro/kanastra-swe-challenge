from src.handlers.abstract_handler import AbstractHandler
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage
from src.models.debit_details import DebitDetails
from src.models.data_status import DataStatus


class ContextBuilderHandler(AbstractHandler):
    def handle(self, sqs_message: SQSMessage,  data_context: DataContext = None) -> DataContext:
        self.logger.debug('Building context', extra={'sqs_message': sqs_message.content})
        context = DataContext()

        if not sqs_message.receipt_handle or not sqs_message.body:
            self.logger.error('Invalid SQS message', extra={'sqs_message': sqs_message.content})
            context.status = DataStatus.INVALID
            return super().handle(sqs_message,  context)

        splited_body = sqs_message.body.split(',')

        if len(splited_body) != 6:
            self.logger.error('Invalid SQS message content', extra={'sqs_message': sqs_message.content})
            context.status = DataStatus.INVALID
            return super().handle(sqs_message,  context)

        try:
            debit_details = DebitDetails()
            debit_details.name = splited_body[0]
            debit_details.government_id = int(splited_body[1])
            debit_details.email = splited_body[2]
            debit_details.debt_amount = float(splited_body[3])
            debit_details.debt_due_date = splited_body[4]
            debit_details.debt_id = splited_body[5]

            context.debit_details = debit_details
            context.status = DataStatus.VALID
        except Exception as e:
            self.logger.error('Invalid SQS message content', extra={'sqs_message': sqs_message.content})
            context.status = DataStatus.INVALID

        return super().handle(sqs_message,  context)
