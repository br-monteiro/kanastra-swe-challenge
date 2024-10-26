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
    redis_connection_max_retries: int = int(getenv("REDIS_CONNECTION_MAX_RETRIES", 3))
    redis_connection_retry_interval: int = int(getenv("REDIS_CONNECTION_RETRY_INTERVAL", 5))
    redis_host: str = getenv("REDIS_HOST", "")
    redis_port: int = int(getenv("REDIS_PORT", 6379))
    redis_db: int = int(getenv("REDIS_DB", 0))
    redis_connect_timeout: int = int(getenv("REDIS_CONNECT_TIMEOUT", 5))
    redis_operation_timeout: int = int(getenv("REDIS_OPERATION_TIMEOUT", 5))
    redis_data_expiration: int = int(getenv("REDIS_DATA_EXPIRATION", 3600))


@lru_cache()
def get_settings():
    return Settings()
