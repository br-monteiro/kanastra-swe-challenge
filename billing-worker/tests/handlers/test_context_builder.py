import pytest
from unittest.mock import MagicMock
from src.handlers.context_builder_handler import ContextBuilderHandler
from src.models.data_status import DataStatus


@pytest.fixture
def settings():
    return MagicMock()


@pytest.fixture
def sqs_message():
    body = 'John Doe,11111111111,johndoe@kanastra.com.br,1000000.00,2022-10-12,1adb6ccf-ff16-467f-bea7-5f05d494280f'
    return MagicMock(body=body, receipt_handle='1234567890')


def test_handle_valid_message(settings, sqs_message):
    handler = ContextBuilderHandler(settings)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message)

    assert context.status == DataStatus.VALID
    assert context.bill_details.name == 'John Doe'
    assert context.bill_details.government_id == 11111111111
    assert context.bill_details.email == 'johndoe@kanastra.com.br'
    assert context.bill_details.debt_amount == 1000000.00
    assert context.bill_details.debt_due_date == '2022-10-12'
    assert context.bill_details.debt_id == '1adb6ccf-ff16-467f-bea7-5f05d494280f'
    handler.logger.error.assert_not_called()


def test_handle_invalid_message(settings, sqs_message):
    sqs_message.body = None
    handler = ContextBuilderHandler(settings)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message)

    assert context.status == DataStatus.INVALID
    handler.logger.error.assert_called_once_with(
        'Invalid SQS message', extra={'sqs_message': sqs_message.content})


def test_handle_invalid_message_content(settings, sqs_message):
    sqs_message.body = 'John Doe,11111111111'
    handler = ContextBuilderHandler(settings)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message)

    assert context.status == DataStatus.INVALID
    handler.logger.error.assert_called_once_with(
        'Invalid SQS message content', extra={'sqs_message': sqs_message.content})


def test_handle_invalid_message_content_type(settings, sqs_message):
    sqs_message.body = 'John Doe,AAAA,johndoe@kanastra.com.br,1000000.00,2022-10-12,1adb6ccf-ff16-467f-bea7-5f05d494280f'
    handler = ContextBuilderHandler(settings)
    handler.logger = MagicMock()
    context = handler.handle(sqs_message)

    assert context.status == DataStatus.INVALID
    handler.logger.error.assert_called_once_with(
        'Invalid SQS message content', extra={'sqs_message': sqs_message.content})
