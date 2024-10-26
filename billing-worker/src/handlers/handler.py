from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from src.models.data_context import DataContext
from src.models.sqs_message import SQSMessage


class Handler(ABC):
    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        """
        Set the next handler in the chain.
        """

    @abstractmethod
    def handle(self, sqs_message: SQSMessage,  data_context: DataContext = None) -> DataContext:
        """
        Handle the message and return the result.
        """
