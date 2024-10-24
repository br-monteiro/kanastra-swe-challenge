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
    sqs_client = SQSClient(settings)
    assert sqs_client._client is None
    assert sqs_client.settings == settings
    get_logger.assert_called_with("src.aws.sqs.sqs_client")


@patch("src.aws.sqs.sqs_client.boto3.client")
@patch("src.aws.sqs.sqs_client.get_logger")
def test_create_client(get_logger, boto3_client, settings):
    sqs_client = SQSClient(settings)
    sqs_client.create_client()

    boto3_client.assert_called_with(
        "sqs", region_name="us-east-1",
        endpoint_url="http://localhost:4566"
    )
    get_logger.return_value.info.assert_called_with("SQS client created")


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message(get_logger, settings):
    sqs_client = SQSClient(settings)
    sqs_client._client = MagicMock()
    sqs_client.send_message("http://localhost:4566/queue", "message body")

    sqs_client._client.send_message.assert_called_with(
        QueueUrl="http://localhost:4566/queue",
        MessageBody="message body"
    )
    get_logger.return_value.debug.assert_called_with(
        "Message sent to queue http://localhost:4566/queue",
        extra={"message_body": "message body"}
    )


@patch("src.aws.sqs.sqs_client.get_logger")
def test_send_message_no_client(get_logger, settings):
    sqs_client = SQSClient(settings)
    with pytest.raises(SQSClientException) as exc:
        sqs_client.send_message("http://localhost:4566/queue", "message body")

    assert str(exc.value) == "SQS client not created"
    get_logger.return_value.error.assert_called_with("SQS client not created")


@patch("src.aws.sqs.sqs_client.get_logger")
def test_validate_client(get_logger, settings):
    sqs_client = SQSClient(settings)
    sqs_client._client = MagicMock()
    sqs_client._validate_client()

    get_logger.return_value.error.assert_not_called()


@patch("src.aws.sqs.sqs_client.get_logger")
def test_validate_client_no_client(get_logger, settings):
    sqs_client = SQSClient(settings)
    with pytest.raises(SQSClientException) as exc:
        sqs_client._validate_client()

    assert str(exc.value) == "SQS client not created"
    get_logger.return_value.error.assert_called_with("SQS client not created")
