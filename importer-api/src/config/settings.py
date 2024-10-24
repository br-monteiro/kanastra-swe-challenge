from os import getenv
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: str = getenv("LOG_LEVEL", "INFO")


@lru_cache()
def get_settings():
    return Settings()
