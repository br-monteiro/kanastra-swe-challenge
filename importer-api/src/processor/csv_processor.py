import asyncio
from fastapi import UploadFile
from src.aws.sqs.sqs_client import SQSClient
from src.config.settings import Settings
from src.logger.logger import get_logger


class CSVProcessor:
    def __init__(self, settings: Settings, upload_file: UploadFile, sqs_client: SQSClient):
        self._file_header = None
        self._chunk_size = 1048576  # 1024 * 1024 = 1MB
        self.settings = settings
        self.upload_file = upload_file
        self.sqs_client = sqs_client
        self.logger = get_logger(__name__)

    async def process(self):
        self.logger.debug("Initiating CSV processing")
        messages = []
        semaphore = asyncio.Semaphore(
            self.settings.max_csv_process_concurrent_tasks
        )

        while True:
            chunk = await self.upload_file.read(self._chunk_size)
            if not chunk:
                break

            lines = chunk.decode().splitlines()
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
        self.logger.debug(f"Sending {len(messages)} messages to SQS")

        async with semaphore:
            try:
                await self.sqs_client.send_message_batch(messages)
            except Exception as e:
                self.logger.error(f"Error sending messages: {e}")
                print(f"Erro ao enviar mensagens: {e}")
