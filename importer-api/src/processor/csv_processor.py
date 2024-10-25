import asyncio
from src.aws.sqs.sqs_client import SQSClient
from src.config.settings import Settings
from src.logger.logger import get_logger
from src.metrics.metrics_registry_manager import get_metrics_registry

METRICS = get_metrics_registry()
METRICS.register_counter("csv_processor_messages_sent", "Number of messages sent to SQS")
METRICS.register_counter("csv_processor_messages_failed", "Number of messages failed to send to SQS")
METRICS.register_summary("csv_processor_duration_seconds", "Duration of CSV processing in seconds")

class CSVProcessor:
    def __init__(self, settings: Settings, file_content: bytes, sqs_client: SQSClient):
        self.settings = settings
        self.file_content = file_content
        self.sqs_client = sqs_client
        self.logger = get_logger(__name__)

    @METRICS.get("csv_processor_duration_seconds").time()
    async def process(self):
        self.logger.debug("Initiating CSV processing")
        messages = []
        semaphore = asyncio.Semaphore(
            self.settings.max_csv_process_concurrent_tasks
        )

        lines = self.file_content.decode().splitlines()

        for line in lines:
            normalized_line = line.strip()
            messages.append(normalized_line)

            if self._is_message_buffer_full(messages):
                await self._send_batch_messages(semaphore, messages)
                messages = []


        if messages:
            await self._send_batch_messages(semaphore, messages)

    def _is_message_buffer_full(self, messages: list):
        return len(messages) >= self.settings.max_sqs_send_message_batch_size

    async def _send_batch_messages(self, semaphore: asyncio.Semaphore, messages: list):
        async with semaphore:
            try:
                self.sqs_client.send_message_batch(messages)
                METRICS.get("csv_processor_messages_sent").inc(len(messages))
            except Exception as e:
                self.logger.error(f"Error sending messages: {e}")
                METRICS.get("csv_processor_messages_failed").inc(len(messages))
