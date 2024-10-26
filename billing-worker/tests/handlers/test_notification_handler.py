import pytest
from unittest.mock import MagicMock
from src.handlers.notification_handler import NotificationHandler
from src.models.data_status import DataStatus
from src.models.bill_details import BillDetails


@pytest.fixture
def settings():
    return MagicMock(redis_data_expiration=60)


@pytest.fixture
def cache_client():
    return MagicMock()


@pytest.fixture
def sns_client():
    return MagicMock()


@pytest.fixture
def sqs_message():
    return MagicMock(content='message_test')


@pytest.fixture
def data_context():
    bill_details = BillDetails()
    bill_details.debt_id = 'kanastra-123'

    return MagicMock(bill_details=bill_details)


def test_handle(settings, cache_client, sns_client, sqs_message, data_context):
    cache_client.get.return_value = None
    data_context.status = DataStatus.VALID

    handler = NotificationHandler(settings, cache_client, sns_client)
    handler.logger = MagicMock()
    handler.notify = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    handler.logger.debug.assert_any_call(
        'Notification', extra={'sqs_message': 'message_test'})
    cache_client.set.assert_called_once_with(
        'notification:kanastra-123', 1, 60)
    handler.notify.assert_called_once_with(data_context)


def test_handle_invalid_context(settings, cache_client, sns_client, sqs_message, data_context):
    data_context.status = DataStatus.INVALID

    handler = NotificationHandler(settings, cache_client, sns_client)
    handler.logger = MagicMock()
    handler.notify = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    cache_client.get.assert_not_called()
    cache_client.set.assert_not_called()
    handler.notify.assert_not_called()


def test_handle_cached(settings, cache_client, sns_client, sqs_message, data_context):
    cache_client.get.return_value = 1
    data_context.status = DataStatus.VALID

    handler = NotificationHandler(settings, cache_client, sns_client)
    handler.logger = MagicMock()
    handler.notify = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    cache_client.get.assert_called_once_with('notification:kanastra-123')
    cache_client.set.assert_not_called()
    handler.notify.assert_not_called()


def test_notify(settings, cache_client, sns_client, data_context):
    handler = NotificationHandler(settings, cache_client, sns_client)
    handler.logger = MagicMock()
    handler.notify(data_context)

    handler.logger.debug.assert_called_once_with(
        'Sending notification', extra={'debt_id': 'kanastra-123'})
    sns_client.publish.assert_called_once_with(
        '{"debt_id": "kanastra-123"}')