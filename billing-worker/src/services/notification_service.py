import threading
from src.config.settings import Settings
from src.aws.sns.sns_client import SNSClient


class NotificationService:
    _instance = None

    def __new__(cls, settings: Settings, sns_client: SNSClient):
        if not cls._instance:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance.settings = settings
            cls._instance.sns_client = sns_client
            cls._instance._buffer = []
        return cls._instance

    def enqueue(self, message: str):
        self._buffer.append(message)
        return self

    def flush(self):
        self._send()
        buffer_size = len(self._buffer)

        if buffer_size > 0:
            self.sns_client.publish_batch(self._buffer)
            self._buffer = []

        """
        Schedule the next flush
        This necessary to avoid blocking the main thread and to ensure that the buffer is flushed periodically
        """
        threading.Timer(
            self.settings.notification_flush_interval, self.flush).start()

    def _send(self):
        buffer_size = len(self._buffer)

        if buffer_size >= self.settings.max_sns_send_message_batch_size:
            self.sns_client.publish_batch(self._buffer)
            self._buffer = []
