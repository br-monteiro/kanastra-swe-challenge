import pytest
from unittest.mock import AsyncMock, patch
from src.api.file_importer.tasks import process_file_task


@patch("src.api.file_importer.tasks.settings")
@patch("src.api.file_importer.tasks.SQSClient")
@patch("src.api.file_importer.tasks.CSVProcessor")
@pytest.mark.asyncio
async def test_process_file_task(csv_processor, sqs_client, settings):
    settings.sqs_queue_url = "test_queue_url"
    csv_processor.return_value.process = AsyncMock()

    file_content = b"line1\nline2\nline3"

    await process_file_task(file_content)

    sqs_client.assert_called_once_with(settings.sqs_queue_url, settings)
    sqs_client.return_value.create_client.assert_called_once()
    csv_processor.assert_called_once_with(
        settings, file_content,
        sqs_client.return_value
    )
    csv_processor.return_value.process.assert_awaited_once()
