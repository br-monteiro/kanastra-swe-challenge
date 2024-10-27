from src.config.settings import Settings
from src.models.sqs_message import SQSMessage
from src.metrics.metrics_registry_manager import get_metrics_registry
from src.logger.logger import get_logger


METRICS = get_metrics_registry()
METRICS.register_counter("mails_sent", "Mails sent")


class SendMailService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)

    def send_mail(self, sqs_message: SQSMessage):
        """
        Do some magic to send the mail
        """
        self.logger.debug(f"Mail sent: {sqs_message.body}")
        METRICS.get("mails_sent").inc()