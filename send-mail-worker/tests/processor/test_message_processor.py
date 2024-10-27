import pytest
from unittest.mock import MagicMock, patch
from src.processors.message_processor import MessageProcessor


@pytest.fixture
def send_mail_service():
    return MagicMock()


@pytest.fixture
def sqs_consumer():
    return MagicMock()


@patch("src.processors.message_processor.get_logger")
def test_init(get_logger, send_mail_service, sqs_consumer):
    message_processor = MessageProcessor(send_mail_service, sqs_consumer)

    assert message_processor.send_mail_service == send_mail_service
    assert message_processor.sqs_consumer == sqs_consumer
    get_logger.assert_called_once_with("src.processors.message_processor")


@patch("src.processors.message_processor.METRICS")
@patch("src.processors.message_processor.get_logger")
def test_process(get_logger, metrics, send_mail_service, sqs_consumer):
    message1 = MagicMock(body="message1")
    message2 = MagicMock(body="message2")
    sqs_consumer.consume.return_value = [message1, message2]

    message_processor = MessageProcessor(send_mail_service, sqs_consumer)
    message_processor.process()

    sqs_consumer.consume.assert_called_once()
    sqs_consumer.delete_message.assert_any_call(message1)
    sqs_consumer.delete_message.assert_any_call(message2)
    send_mail_service.send_mail.assert_any_call(message1)
    send_mail_service.send_mail.assert_any_call(message2)
    get_logger.return_value.debug.assert_any_call(
        "Starting message processing")
    get_logger.return_value.debug.assert_any_call(
        "Processing message: message1")
    get_logger.return_value.debug.assert_any_call(
        "Processing message: message2")
    get_logger.return_value.error.assert_not_called()
    metrics.get("messages_processed_successfully").inc.assert_any_call()

@patch("src.processors.message_processor.METRICS")
@patch("src.processors.message_processor.get_logger")
def test_process_error(get_logger, metrics, send_mail_service, sqs_consumer):
    message1 = MagicMock(body="message1")
    message2 = MagicMock(body="message2")
    send_mail_service.send_mail.side_effect = Exception("error")
    sqs_consumer.consume.return_value = [message1, message2]

    message_processor = MessageProcessor(send_mail_service, sqs_consumer)
    message_processor.process()

    sqs_consumer.consume.assert_called_once()
    sqs_consumer.delete_message.assert_any_call(message1)
    sqs_consumer.delete_message.assert_any_call(message2)
    get_logger.return_value.debug.assert_any_call(
        "Starting message processing")
    get_logger.return_value.debug.assert_any_call(
        "Processing message: message1")
    get_logger.return_value.debug.assert_any_call(
        "Processing message: message2")
    get_logger.return_value.error.assert_any_call(
        "Error processing message: error")
    metrics.get.assert_called_with("messages_processed_errors")
