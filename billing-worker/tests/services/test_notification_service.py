import pytest
from unittest.mock import MagicMock, patch
from src.services.notification_service import NotificationService


@pytest.fixture
def settings():
    return MagicMock(notification_flush_interval=7, max_sns_send_message_batch_size=3)


@pytest.fixture
def sns_client():
    return MagicMock()


@pytest.fixture(autouse=True)
def before_each():
    NotificationService._instance = None


def test_singleton(settings, sns_client):
    service1 = NotificationService(settings, sns_client)
    service2 = NotificationService(settings, sns_client)

    assert service1 is service2


def test_enqueue(settings, sns_client):
    service = NotificationService(settings, sns_client)
    service.enqueue("message")
    assert service._buffer == ["message"]


@patch("src.services.notification_service.threading")
def test_flush(threading, settings, sns_client):
    service = NotificationService(settings, sns_client)
    service._buffer = ["message1", "message2"]

    service.flush()

    assert service._buffer == []
    threading.Timer.assert_called_once_with(7, service.flush)
    service.sns_client.publish_batch.assert_called_once_with(
        ["message1", "message2"])


@patch("src.services.notification_service.threading")
def test_flush_when_buffer_is_empty(threading, settings, sns_client):
    service = NotificationService(settings, sns_client)
    service._buffer = []

    service.flush()

    assert service._buffer == []
    threading.Timer.assert_called_once_with(7, service.flush)
    service.sns_client.publish_batch.assert_not_called()


def test_send(settings, sns_client):
    service = NotificationService(settings, sns_client)
    service._buffer = ["message1", "message2", "message3"]

    service._send()

    assert service._buffer == []
    service.sns_client.publish_batch.assert_called_once_with(
        ["message1", "message2", "message3"])


def test_send_when_buffer_is_empty(settings, sns_client):
    service = NotificationService(settings, sns_client)
    service._buffer = []

    service._send()

    assert service._buffer == []
    service.sns_client.publish_batch.assert_not_called()


def test_send_when_buffer_is_less_than_batch_size(settings, sns_client):
    service = NotificationService(settings, sns_client)
    service._buffer = ["message1", "message2"]

    service._send()

    assert service._buffer == ["message1", "message2"]
    service.sns_client.publish_batch.assert_not_called()
