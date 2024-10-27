import pytest
from unittest.mock import MagicMock, patch
from src.aws.sns.sns_client import SNSClient


@pytest.fixture
def settings():
    _settings = MagicMock()
    _settings.aws_region = "us-east-1"
    _settings.sns_endpoint_url = "http://localhost:4566"
    return _settings


@patch("src.aws.sns.sns_client.get_logger")
def test_init(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)

    assert sns_client._client is None
    assert sns_client.topic_arn == "arn:aws:sns:us-east-1:123456789012:topic"
    assert sns_client.settings == settings
    get_logger.assert_called_once_with("src.aws.sns.sns_client")


@patch("src.aws.sns.sns_client.boto3.client")
@patch("src.aws.sns.sns_client.get_logger")
def test_create_client(get_logger, boto3_client, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)
    sns_client.create_client()

    boto3_client.assert_called_once_with(
        "sns",
        region_name="us-east-1",
        endpoint_url="http://localhost:4566"
    )
    assert sns_client._client == boto3_client.return_value


@patch("src.aws.sns.sns_client.get_logger")
def test_publish(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)
    sns_client._client = MagicMock()
    sns_client.publish("Kanastra")

    sns_client._client.publish.assert_called_once_with(
        TopicArn="arn:aws:sns:us-east-1:123456789012:topic",
        Message="Kanastra"
    )
    get_logger.return_value.debug.assert_called_once_with(
        "Message published to topic arn:aws:sns:us-east-1:123456789012:topic",
        extra={"content": "Kanastra"}
    )


@patch("src.aws.sns.sns_client.get_logger")
def test_publish_no_client(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)

    with pytest.raises(Exception) as exc:
        sns_client.publish("Kanastra")

    assert str(exc.value) == "SNS client not created"
    get_logger.return_value.error.assert_called_once_with(
        "SNS client not created")


@patch("src.aws.sns.sns_client.get_logger")
def test_publish_batch(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)
    sns_client._client = MagicMock()
    sns_client.publish_batch(["Kanastra", "Kanastra"])

    sns_client._client.publish_batch.assert_called_once_with(
        TopicArn="arn:aws:sns:us-east-1:123456789012:topic",
        PublishBatchRequestEntries=[
            {"Id": "0", "Message": "Kanastra"},
            {"Id": "1", "Message": "Kanastra"}
        ]
    )
    get_logger.return_value.debug.assert_called_once_with(
        "Messages published to topic arn:aws:sns:us-east-1:123456789012:topic",
        extra={"messages": ["Kanastra", "Kanastra"]}
    )


@patch("src.aws.sns.sns_client.get_logger")
def test_publish_batch_no_client(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)

    with pytest.raises(Exception) as exc:
        sns_client.publish_batch(["Kanastra", "Kanastra"])

    assert str(exc.value) == "SNS client not created"
    get_logger.return_value.error.assert_called_once_with(
        "SNS client not created")


@patch("src.aws.sns.sns_client.get_logger")
def test_publish_batch_error(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)
    sns_client._client = MagicMock()
    sns_client._client.publish_batch.side_effect = Exception("Error")

    sns_client.publish_batch(["Kanastra", "Kanastra"])

    get_logger.return_value.error.assert_called_once_with(
        "Error publishing messages to topic arn:aws:sns:us-east-1:123456789012:topic",
        extra={
            "messages": ["Kanastra", "Kanastra"],
            "error": "Error"
        }
    )


@patch("src.aws.sns.sns_client.get_logger")
def test_validate_client(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)
    sns_client._client = MagicMock()

    sns_client._validate_client()

    get_logger.return_value.error.assert_not_called()


@patch("src.aws.sns.sns_client.get_logger")
def test_validate_client_no_client(get_logger, settings):
    sns_client = SNSClient(
        "arn:aws:sns:us-east-1:123456789012:topic", settings)

    with pytest.raises(Exception) as exc:
        sns_client._validate_client()

    assert str(exc.value) == "SNS client not created"
    get_logger.return_value.error.assert_called_once_with(
        "SNS client not created")
