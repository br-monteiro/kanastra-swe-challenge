import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.processor.csv_processor import CSVProcessor


@pytest.fixture
def settings():
    _settings = MagicMock()
    _settings.max_csv_process_concurrent_tasks = 5
    _settings.max_sqs_send_message_batch_size = 10
    return _settings


@pytest.fixture
def sqs_client():
    return AsyncMock()


@pytest.fixture
def csv_processor(settings, sqs_client):
    file_content = b"line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\nline11"
    return CSVProcessor(settings, file_content, sqs_client)


@patch("src.processor.csv_processor.get_logger")
def test_init(get_logger, settings, sqs_client):
    file_content = b"line1\nline2\nline3"
    csv_processor = CSVProcessor(settings, file_content, sqs_client)

    assert csv_processor.settings == settings
    assert csv_processor.file_content == file_content
    assert csv_processor.sqs_client == sqs_client
    assert csv_processor.logger == get_logger.return_value
    get_logger.assert_called_once_with("src.processor.csv_processor")


@patch("src.processor.csv_processor.METRICS")
@pytest.mark.asyncio
async def test_process_full_batch(mock_metrics, csv_processor, sqs_client):
    mock_metrics.get.return_value.time.return_value = AsyncMock()
    mock_metrics.get.return_value.inc = MagicMock()

    await csv_processor.process()

    assert sqs_client.send_message_batch.call_count == 2
    mock_metrics.get("csv_processor_messages_sent").inc.assert_any_call(10)
    mock_metrics.get("csv_processor_messages_sent").inc.assert_any_call(1)


@patch("src.processor.csv_processor.METRICS")
@pytest.mark.asyncio
async def test_process_handles_empty_file(mock_metrics, settings, sqs_client):
    csv_processor = CSVProcessor(settings, b"", sqs_client)
    await csv_processor.process()

    sqs_client.send_message_batch.assert_not_called()
    mock_metrics.get("csv_processor_messages_sent").inc.assert_not_called()
    mock_metrics.get("csv_processor_messages_failed").inc.assert_not_called()


@patch("src.processor.csv_processor.METRICS")
@pytest.mark.asyncio
async def test_process_handles_failed_send(mock_metrics, csv_processor, sqs_client):
    sqs_client.send_message_batch.side_effect = Exception("SQS error")

    await csv_processor.process()

    mock_metrics.get("csv_processor_messages_failed").inc.assert_called_with(
        1)


@patch("src.processor.csv_processor.METRICS")
@pytest.mark.asyncio
async def test_process_semaphore_limited_concurrency(mock_metrics, settings, sqs_client):
    settings.max_csv_process_concurrent_tasks = 1
    file_content = b"line1\nline2\nline3"
    csv_processor = CSVProcessor(settings, file_content, sqs_client)

    await csv_processor.process()

    sqs_client.send_message_batch.assert_called_once()


@patch("src.processor.csv_processor.METRICS")
@pytest.mark.asyncio
async def test_send_batch_messages(mock_metrics, csv_processor, sqs_client):
    messages = ["message1", "message2", "message3"]
    semaphore = MagicMock()

    await csv_processor._send_batch_messages(semaphore, messages)

    sqs_client.send_message_batch.assert_called_once_with(messages)
    mock_metrics.get("csv_processor_messages_sent").inc.assert_called_with(3)


@patch("src.processor.csv_processor.METRICS")
@pytest.mark.asyncio
async def test_send_batch_messages_handles_exception(mock_metrics, csv_processor, sqs_client):
    messages = ["message1", "message2", "message3"]
    semaphore = MagicMock()
    sqs_client.send_message_batch.side_effect = Exception("SQS error")

    await csv_processor._send_batch_messages(semaphore, messages)

    mock_metrics.get("csv_processor_messages_failed").inc.assert_called_with(3)
