from fastapi import APIRouter, Depends, UploadFile
from src.processor.csv_processor import CSVProcessor
from src.aws.sqs.sqs_client import SQSClient
from src.config.settings import get_settings


def sqs_client_factory():
    settings = get_settings()
    sqs_client = SQSClient(settings.sqs_queue_url, settings)
    sqs_client.create_client()
    return sqs_client


def csv_processor_factory(file: UploadFile, sqs_client: SQSClient = Depends(sqs_client_factory)):
    settings = get_settings()
    return CSVProcessor(settings, file, sqs_client)


router = APIRouter()


@router.post('/v1/upload')
async def upload_file(csv_processor: CSVProcessor = Depends(csv_processor_factory)):
    await csv_processor.process()
    return {"status": "file processed"}
