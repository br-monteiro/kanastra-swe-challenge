from src.aws.sqs.sqs_client import SQSClient
from src.config.settings import get_settings
from src.processor.csv_processor import CSVProcessor


settings = get_settings()


async def process_file_task(file_content):
    sqs_client = SQSClient(settings.sqs_queue_url, settings)
    sqs_client.create_client()

    processor = CSVProcessor(settings, file_content, sqs_client)
    await processor.process()
