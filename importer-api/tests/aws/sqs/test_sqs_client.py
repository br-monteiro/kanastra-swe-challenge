import pytest
from unittest.mock import MagicMock, patch
from src.aws.sqs.sqs_client import SQSClient
from src.aws.sqs.exceptions.sqs_client_exception import SQSClientException


@pytest.fixture
def settings():
    _settings = MagicMock()
    _settings.aws_region = "us-east-1"
    _settings.sqs_endpoint_url = "http://localhost:4566"
    return _settings


@patch("src.aws.sqs.sqs_client.get_logger")
def test_init(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    assert sqs_client._client is None
    assert sqs_client.queue_url == "http://localhost:4566/queue"
    assert sqs_client.settings == settings
    get_logger.assert_called_with("src.aws.sqs.sqs_client")


@patch("src.aws.sqs.sqs_client.boto3.client")
@patch("src.aws.sqs.sqs_client.get_logger")
def test_create_client(get_logger, boto3_client, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    sqs_client.create_client()

    boto3_client.assert_called_with(
        "sqs", region_name="us-east-1",
        endpoint_url="http://localhost:4566"
    )
    get_logger.return_value.info.assert_called_with("SQS client created")


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    sqs_client._client = MagicMock()
    sqs_client.send_message("message body")

    sqs_client._client.send_message.assert_called_with(
        QueueUrl="http://localhost:4566/queue",
        MessageBody="message body"
    )
    get_logger.return_value.debug.assert_called_with(
        "Message sent to queue http://localhost:4566/queue",
        extra={"message_body": "message body"}
    )


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message_exception(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    sqs_client._client = MagicMock()
    sqs_client._client.send_message.side_effect = Exception("error")
    sqs_client.send_message("message body")

    sqs_client._client.send_message.assert_called_with(
        QueueUrl="http://localhost:4566/queue",
        MessageBody="message body"
    )
    get_logger.return_value.error.assert_called_with(
        "Error sending message to queue http://localhost:4566/queue",
        extra={
            "message_body": "message body",
            "error": "error"
        }
    )


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message_batch(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    sqs_client._client = MagicMock()
    sqs_client.send_message_batch(["message1", "message2"])

    sqs_client._client.send_message_batch.assert_called_with(
        QueueUrl="http://localhost:4566/queue",
        Entries=[
            {"Id": "0", "MessageBody": "message1"},
            {"Id": "1", "MessageBody": "message2"}
        ]
    )
    get_logger.return_value.debug.assert_called_with(
        "Messages sent to queue http://localhost:4566/queue",
        extra={"messages": ["message1", "message2"]}
    )


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message_batch_exception(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    sqs_client._client = MagicMock()
    sqs_client._client.send_message_batch.side_effect = Exception("error")
    sqs_client.send_message_batch(["message1", "message2"])

    sqs_client._client.send_message_batch.assert_called_with(
        QueueUrl="http://localhost:4566/queue",
        Entries=[
            {"Id": "0", "MessageBody": "message1"},
            {"Id": "1", "MessageBody": "message2"}
        ]
    )
    get_logger.return_value.error.assert_called_with(
        "Error sending messages to queue http://localhost:4566/queue",
        extra={
            "messages": ["message1", "message2"],
            "error": "error"
        }
    )


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message_no_client(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    with pytest.raises(SQSClientException) as exc:
        sqs_client.send_message("message body")

    assert str(exc.value) == "SQS client not created"
    get_logger.return_value.error.assert_called_with("SQS client not created")


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message_no_client(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    with pytest.raises(SQSClientException) as exc:
        sqs_client.send_message("message body")

    assert str(exc.value) == "SQS client not created"
    get_logger.return_value.error.assert_called_with("SQS client not created")


@patch("src.aws.sqs.sqs_client.get_logger")
def test_validate_client(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    sqs_client._client = MagicMock()
    sqs_client._validate_client()

    get_logger.return_value.error.assert_not_called()


@patch("src.aws.sqs.sqs_client.get_logger")
def test_validate_client_no_client(get_logger, settings):
    sqs_client = SQSClient("http://localhost:4566/queue", settings)
    with pytest.raises(SQSClientException) as exc:
        sqs_client._validate_client()

    assert str(exc.value) == "SQS client not created"
    get_logger.return_value.error.assert_called_with("SQS client not created")
