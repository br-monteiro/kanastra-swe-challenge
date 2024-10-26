from os import getenv
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: str = getenv("LOG_LEVEL", "INFO")
    aws_region: str = getenv("AWS_REGION", "us-east-1")
    sqs_queue_url: str = getenv("SQS_QUEUE_URL", "")
    sqs_endpoint_url: str = getenv("SQS_ENDPOINT_URL", "")
    sqs_max_messages: int = int(getenv("SQS_MAX_MESSAGES", 10))
    sqs_wait_time_seconds: int = int(getenv("SQS_WAIT_TIME_SECONDS", 20))
    sns_endpoint_url: str = getenv("SNS_ENDPOINT_URL", "")
    sns_topic_arn: str = getenv("SNS_TOPIC_ARN", "")


@lru_cache()
def get_settings():
    return Settings()
