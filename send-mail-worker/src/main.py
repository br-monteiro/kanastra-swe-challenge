from prometheus_client import start_http_server
from src.aws.sqs.sqs_consumer import SQSConsumer
from src.config.settings import get_settings
from src.processors.message_processor import MessageProcessor


def main():
    settings = get_settings()

    start_http_server(settings.metrics_port)

    sqs_consumer = SQSConsumer(settings)
    sqs_consumer.create_client()

    message_processor = MessageProcessor(sqs_consumer)
    message_processor.process()


if __name__ == "__main__":
    main()
