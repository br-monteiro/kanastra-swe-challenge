import pytest
from src.handlers.handler import Handler


def test_init():
    with pytest.raises(TypeError):
        Handler()


def test_concrete_handler_implementation():
    class ConcreteHandler(Handler):
        def set_next(self, handler: Handler) -> Handler:
            return handler

        def handle(self, sqs_message, data_context):
            return data_context

    handler = ConcreteHandler()
    assert handler.handle(None, None) is None
    assert handler.set_next(None) is None
