from src.aws.sqs.sqs_consumer import SQSConsumer
from src.logger.logger import get_logger
from src.metrics.metrics_registry_manager import get_metrics_registry
from src.services.send_mail_service import SendMailService


METRICS = get_metrics_registry()
METRICS.register_counter("messages_processed_successfully", "Messages processed successfully")
METRICS.register_counter("messages_processed_errors", "Messages processed with errors")


class MessageProcessor:
    def __init__(self, send_mail_service: SendMailService, sqs_consumer: SQSConsumer):
        self.send_mail_service = send_mail_service
        self.sqs_consumer = sqs_consumer
        self.logger = get_logger(__name__)

    def process(self):
        self.logger.debug("Starting message processing")
        for message in self.sqs_consumer.consume():
            try:
                self.logger.debug(f"Processing message: {message.body}")
                self.send_mail_service.send_mail(message)
                METRICS.get("messages_processed_successfully").inc()
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                METRICS.get("messages_processed_errors").inc()

            self.sqs_consumer.delete_message(message)
