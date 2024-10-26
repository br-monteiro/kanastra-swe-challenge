import pytest
from unittest.mock import MagicMock
from src.handlers.check_billing_handler import CheckBillingHandler
from src.models.data_status import DataStatus


@pytest.fixture
def settings():
    return MagicMock()


@pytest.fixture
def cache_client():
    return MagicMock()


@pytest.fixture
def sqs_message():
    return MagicMock(content='message_test')


@pytest.fixture
def data_context():
    bill_details = MagicMock(debt_id='kanastra-123')
    return MagicMock(bill_details=bill_details)


def test_handle(settings, cache_client, sqs_message, data_context):
    data_context.status = DataStatus.VALID
    data_context.bill_details.has_been_processed = False
    cache_client.get.return_value = None

    handler = CheckBillingHandler(settings, cache_client)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    handler.logger.debug.assert_called_once_with(
        'Check billing process', extra={'sqs_message': 'message_test'})
    cache_client.get.assert_called_once_with('kanastra-123')


def test_handle_invalid_context(settings, cache_client, sqs_message, data_context):
    data_context.status = DataStatus.INVALID

    handler = CheckBillingHandler(settings, cache_client)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    handler.logger.debug.assert_any_call(
        'Invalid context', extra={'sqs_message': 'message_test'})
    cache_client.get.assert_not_called()


def test_handle_bill_already_processed(settings, cache_client, sqs_message, data_context):
    data_context.status = DataStatus.VALID
    data_context.bill_details.has_been_processed = True

    handler = CheckBillingHandler(settings, cache_client)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    handler.logger.debug.assert_any_call(
        'Bill already processed', extra={'sqs_message': 'message_test'})
    cache_client.get.assert_not_called()
    assert context.status == DataStatus.SKIPPED


def test_handle_bill_already_processed_in_cache(settings, cache_client, sqs_message, data_context):
    data_context.status = DataStatus.VALID
    data_context.bill_details.has_been_processed = False
    cache_client.get.return_value = 'processed'

    handler = CheckBillingHandler(settings, cache_client)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    handler.logger.debug.assert_any_call(
        'Bill already processed', extra={'sqs_message': 'message_test'})
    cache_client.get.assert_called_once_with('kanastra-123')
    handler.logger.debug.assert_any_call(
        'Bill already processed', extra={'sqs_message': 'message_test'})
    cache_client.get.assert_called_once_with('kanastra-123')
    assert context.status == DataStatus.SKIPPED
