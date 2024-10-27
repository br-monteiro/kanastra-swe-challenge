from unittest.mock import patch
from src.main import main


@patch('src.main.start_http_server')
@patch('src.main.SQSConsumer')
@patch('src.main.get_settings')
@patch('src.main.MessageProcessor')
@patch('src.main.SendMailService')
def test_main(
    mock_send_mail_service,
    mock_message_processor,
    mock_get_settings,
    mock_sqs_consumer,
    mock_start_http_server
):
    main()

    settings = mock_get_settings.return_value

    mock_start_http_server.assert_called_with(settings.metrics_port)

    mock_sqs_consumer.assert_called_with(settings)
    mock_sqs_consumer.return_value.create_client.assert_called_once()

    mock_send_mail_service.assert_called_with(settings)

    mock_message_processor.assert_called_with(mock_send_mail_service.return_value, mock_sqs_consumer.return_value)
    mock_message_processor.return_value.process.assert_called_once()
