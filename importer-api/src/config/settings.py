from os import getenv
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = getenv("AWS_REGION", "us-east-1")
    log_level: str = getenv("LOG_LEVEL", "INFO")
    max_csv_process_concurrent_tasks: int = int(getenv("MAX_CSV_PROCESS_CONCURRENT_TASKS", 250))
    max_sqs_send_message_batch_size: int = int(getenv("MAX_SQS_SEND_MESSAGE_BATCH_SIZE", 10))
    sqs_endpoint_url: str = getenv("SQS_ENDPOINT_URL", "")
    sqs_queue_url: str = getenv("SQS_QUEUE_URL", "")


@lru_cache()
def get_settings():
    return Settings()
