from os import getenv
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = getenv("AWS_REGION", "us-east-1")
    log_level: str = getenv("LOG_LEVEL", "INFO")
    sqs_endpoint_url: str = getenv("SQS_ENDPOINT_URL", "")
    sqs_queue_url: str = getenv("SQS_QUEUE_URL", "")


@lru_cache()
def get_settings():
    return Settings()
