import pytest
from unittest.mock import MagicMock, patch
from src.aws.sqs.exceptions.sqs_consumer_exception import SQSConsumerException
from src.aws.sqs.sqs_consumer import SQSConsumer
from src.config.settings import Settings
from src.models.sqs_message import SQSMessage


@pytest.fixture
def settings():
    _settings = Settings()
    _settings.aws_region = "aws_region"
    _settings.sqs_queue_url = "sqs_queue_url"
    _settings.sqs_endpoint_url = None
    return _settings


@patch("src.aws.sqs.sqs_consumer.get_logger")
def test_init(get_logger, settings):
    consumer = SQSConsumer(settings)
    assert consumer.settings == settings
    assert consumer._client is None
    assert consumer.logger == get_logger.return_value
    get_logger.assert_called_once_with("src.aws.sqs.sqs_consumer")


@patch("src.aws.sqs.sqs_consumer.get_logger")
@patch("src.aws.sqs.sqs_consumer.boto3")
def test_create_client(boto3, get_logger, settings):
    consumer = SQSConsumer(settings)
    consumer.create_client()
    assert consumer._client == boto3.client.return_value
    boto3.client.assert_called_once_with(
        "sqs", region_name="aws_region", endpoint_url=None)
    get_logger.return_value.info.assert_called_once_with("Client created")


def test_consume(settings):
    consumer = SQSConsumer(settings)
    consumer._validate_client = MagicMock()
    consumer._get_messages = MagicMock(return_value=[
        {"Body": 'test_message_1'},
        {"Body": 'test_message_2'},
        {"invalid": 'test_message_3'}
    ])
    messages = list(consumer.consume(run_forever=False))

    assert messages[0].content == {"Body": 'test_message_1'}
    assert messages[1].content == {"Body": 'test_message_2'}
    assert messages[2].content == {"invalid": 'test_message_3'}

    assert len(messages) == 3
    consumer._validate_client.assert_called_once()
    consumer._get_messages.assert_called_once()


@patch("src.aws.sqs.sqs_consumer.get_logger")
def test_delete_message(get_logger, settings):
    consumer = SQSConsumer(settings)
    consumer._validate_client = MagicMock()
    consumer._client = MagicMock()
    consumer._client.delete_message = MagicMock()
    message = SQSMessage({"ReceiptHandle": "receipt_handle"})

    consumer.delete_message(message)

    consumer._validate_client.assert_called_once()
    consumer._client.delete_message.assert_called_once_with(QueueUrl="sqs_queue_url",
                                                            ReceiptHandle="receipt_handle")
    get_logger.return_value.debug.assert_called_once_with(
        "Message deleted", extra={"_message": message.content})


@patch("src.aws.sqs.sqs_consumer.get_logger")
def test_delete_message_error(get_logger, settings):
    consumer = SQSConsumer(settings)
    consumer._validate_client = MagicMock()
    consumer._client = MagicMock()
    exception = Exception("error")
    consumer._client.delete_message = MagicMock(side_effect=exception)
    message = SQSMessage({"ReceiptHandle": "receipt_handle"})

    consumer.delete_message(message)

    consumer._validate_client.assert_called_once()
    consumer._client.delete_message.assert_called_once_with(QueueUrl="sqs_queue_url",
                                                            ReceiptHandle="receipt_handle")
    get_logger.return_value.error.assert_called_once_with(
        "Error deleting message", extra={"error": exception})


def test_get_messages(settings):
    consumer = SQSConsumer(settings)
    consumer._client = MagicMock()
    consumer._client.receive_message = MagicMock(
        return_value={"Messages": [1, 2, 3]})
    assert consumer._get_messages() == [1, 2, 3]
    consumer._client.receive_message.assert_called_once_with(QueueUrl="sqs_queue_url",
                                                             MaxNumberOfMessages=settings.sqs_max_messages,
                                                             WaitTimeSeconds=settings.sqs_wait_time_seconds)


def test_get_messages_no_messages(settings):
    consumer = SQSConsumer(settings)
    consumer._client = MagicMock()
    consumer._client.receive_message = MagicMock(return_value={})
    assert consumer._get_messages() == []
    consumer._client.receive_message.assert_called_once_with(QueueUrl="sqs_queue_url",
                                                             MaxNumberOfMessages=settings.sqs_max_messages,
                                                             WaitTimeSeconds=settings.sqs_wait_time_seconds)


def test_validate_client_has_client(settings):
    consumer = SQSConsumer(settings)
    consumer._client = MagicMock()
    consumer._validate_client()


def test_validate_client_no_client(settings):
    consumer = SQSConsumer(settings)
    consumer._client = None
    with pytest.raises(SQSConsumerException) as exc:
        consumer._validate_client()
    assert str(exc.value) == "SQS client not created"
