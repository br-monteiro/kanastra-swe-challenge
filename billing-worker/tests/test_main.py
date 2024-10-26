from unittest.mock import patch
from src.main import main


@patch('src.main.start_http_server')
@patch('src.main.SNSClient')
@patch('src.main.SQSConsumer')
@patch('src.main.RedisClient')
@patch('src.main.get_settings')
@patch('src.main.ContextBuilderHandler')
@patch('src.main.CheckBillingHandler')
@patch('src.main.NotificationHandler')
@patch('src.main.ProcessBillingHandler')
@patch('src.main.MessageProcessor')
def test_main(
    mock_message_processor,
    mock_process_billing_handler,
    mock_notification_handler,
    mock_check_billing_handler,
    mock_context_builder_handler,
    mock_get_settings,
    mock_redis_client,
    mock_sqs_consumer,
    mock_sns_client,
    mock_start_http_server
):
    main()

    settings = mock_get_settings.return_value

    mock_start_http_server.assert_called_with(settings.metrics_port)
    mock_redis_client.assert_called_with(settings)
    mock_sns_client.assert_called_with(settings.sns_topic_arn, settings)
    mock_sns_client.return_value.create_client.assert_called_once()
    mock_sqs_consumer.assert_called_with(settings)
    mock_sqs_consumer.return_value.create_client.assert_called_once()

    mock_context_builder_handler.assert_called_with(settings)
    mock_check_billing_handler.assert_called_with(settings, mock_redis_client.return_value)
    mock_process_billing_handler.assert_called_with(settings, mock_redis_client.return_value)
    mock_notification_handler.assert_called_with(settings, mock_redis_client.return_value, mock_sns_client.return_value)

    mock_message_processor.assert_called_with(mock_context_builder_handler.return_value, mock_sqs_consumer.return_value)
    mock_message_processor.return_value.process.assert_called_once()
