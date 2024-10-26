import pytest
from unittest.mock import MagicMock
from src.handlers.process_billing_handle import ProcessBillingHandler
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
    bill_details.to_json.return_value = 'bill_details_json'

    return MagicMock(bill_details=bill_details)


def test_handle(settings, cache_client, sqs_message, data_context):
    data_context.status = DataStatus.VALID
    data_context.bill_details.has_been_processed = False

    handler = ProcessBillingHandler(settings, cache_client)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    handler.logger.debug.assert_any_call(
        'Process billing', extra={'sqs_message': 'message_test'})
    cache_client.set.assert_called_once_with(
        'kanastra-123', 'bill_details_json')
    assert context.status == DataStatus.PROCESSED
    assert context.bill_details.has_been_processed is True


def test_handle_invalid_context(settings, cache_client, sqs_message, data_context):
    data_context.status = DataStatus.INVALID

    handler = ProcessBillingHandler(settings, cache_client)
    handler.process = MagicMock()

    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    cache_client.set.assert_not_called()
    handler.process.assert_not_called()


def test_handle_skipped_context(settings, cache_client, sqs_message, data_context):
    data_context.status = DataStatus.SKIPPED

    handler = ProcessBillingHandler(settings, cache_client)
    handler.process = MagicMock()

    context = handler.handle(sqs_message, data_context)

    assert context == data_context
    cache_client.set.assert_not_called()
    handler.process.assert_not_called()


def test_process(settings, cache_client, data_context):
    handler = ProcessBillingHandler(settings, cache_client)
    handler.logger = MagicMock()

    result = handler.process(data_context)

    assert result == 'bill_details_json'
    handler.logger.debug.assert_called_once_with(
        'Processing billing', extra={'debt_id': 'kanastra-123'})
    assert data_context.bill_details.has_been_processed is True
