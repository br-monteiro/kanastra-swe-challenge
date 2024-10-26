from prometheus_client import start_http_server
from src.aws.sns.sns_client import SNSClient
from src.aws.sqs.sqs_consumer import SQSConsumer
from src.cache.redis_client import RedisClient
from src.config.settings import get_settings
from src.handlers.check_billing_handler import CheckBillingHandler
from src.handlers.context_builder_handler import ContextBuilderHandler
from src.handlers.notification_handler import NotificationHandler
from src.handlers.process_billing_handler import ProcessBillingHandler
from src.processors.message_processor import MessageProcessor


def main():
    settings = get_settings()

    start_http_server(settings.metrics_port)

    redis_client = RedisClient(settings)

    sns_client = SNSClient(settings.sns_topic_arn, settings)
    sns_client.create_client()

    sqs_consumer = SQSConsumer(settings)
    sqs_consumer.create_client()

    context_builder = ContextBuilderHandler(settings)
    check_billing = CheckBillingHandler(settings, redis_client)
    process_billing = ProcessBillingHandler(settings, redis_client)
    notification = NotificationHandler(settings, redis_client, sns_client)

    context_builder.set_next(check_billing).set_next(
        process_billing).set_next(notification)

    message_processor = MessageProcessor(context_builder, sqs_consumer)
    message_processor.process()


if __name__ == "__main__":
    main()
