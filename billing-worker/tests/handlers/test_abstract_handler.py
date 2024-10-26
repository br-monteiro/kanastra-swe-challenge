import pytest
from unittest.mock import MagicMock, patch
from src.handlers.abstract_handler import AbstractHandler


@pytest.fixture
def settings():
    return MagicMock()


@patch('src.handlers.abstract_handler.get_logger')
def test_init(get_logger, settings):
    class TestHandler(AbstractHandler):
        def handle(self, sqs_message, data_context):
            """
            This method is required to avoid TypeError.
            """

    handler = TestHandler(settings)
    assert handler.settings == settings
    assert handler._next_handler is None
    get_logger.assert_called_once_with('test_abstract_handler')


def test_init_without_handle_method(settings):
    with pytest.raises(TypeError):
        class TestHandler(AbstractHandler):
            """
            This class does not have the handle method.
            """

        TestHandler(settings)


def test_set_next(settings):
    class TestHandler(AbstractHandler):
        def handle(self, sqs_message, data_context):
            """
            This method is required to avoid TypeError.
            """

    handler = TestHandler(settings)
    next_handler = MagicMock()
    assert handler.set_next(next_handler) == next_handler
    assert handler._next_handler == next_handler


def test_handle(settings):
    class TestHandler(AbstractHandler):
        def handle(self, sqs_message, data_context):
            return super().handle(sqs_message, data_context)

    handler = TestHandler(settings)
    sqs_message = MagicMock()
    data_context = MagicMock()
    assert handler.handle(sqs_message, data_context) == data_context
    assert handler._next_handler is None
    next_handler = MagicMock()
    handler.set_next(next_handler)
    assert handler.handle(
        sqs_message, data_context) == next_handler.handle.return_value
    next_handler.handle.assert_called_once_with(sqs_message, data_context)
