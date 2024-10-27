from prometheus_client import start_http_server
from src.aws.sqs.sqs_consumer import SQSConsumer
from src.config.settings import get_settings
from src.processors.message_processor import MessageProcessor
from src.services.send_mail_service import SendMailService


def main():
    settings = get_settings()

    start_http_server(settings.metrics_port)

    sqs_consumer = SQSConsumer(settings)
    sqs_consumer.create_client()

    send_mail_service = SendMailService(settings)

    message_processor = MessageProcessor(send_mail_service, sqs_consumer)
    message_processor.process()


if __name__ == "__main__":
    main()
