from abc import abstractmethod
from src.config.settings import Settings
from src.handlers.handler import Handler
from src.logger.logger import get_logger
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage


class AbstractHandler(Handler):
    def __init__(self, settings: Settings):
        self.settings = settings
        self._next_handler = None
        self.logger = get_logger(self.__class__.__module__)

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, sqs_message: SQSMessage,  data_context: DataContext = None) -> DataContext:
        if self._next_handler:
            return self._next_handler.handle(sqs_message,  data_context)
        return data_context
