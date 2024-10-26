import redis
from time import sleep
from src.logger.logger import get_logger
from src.config.settings import Settings
from src.cache.cache_client import CacheClient
from src.cache.exceptions.cache_operation_exception import CacheOperationException


class RedisClient(CacheClient):
    _instance = None
    logger = get_logger(__name__)

    def __new__(cls, settings: Settings):
        if not cls._instance:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._settings = settings
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        max_retries = self._settings.redis_connection_max_retries
        retry_interval = self._settings.redis_connection_retry_interval

        for attempt in range(max_retries):
            try:
                self.connection = redis.Redis(
                    host=self._settings.redis_host,
                    port=self._settings.redis_port,
                    db=self._settings.redis_db,
                    socket_connect_timeout=self._settings.redis_connect_timeout,
                    socket_timeout=self._settings.redis_operation_timeout
                )

                self.connection.ping()
                return
            except (redis.ConnectionError, redis.TimeoutError) as e:
                self.logger.debug(
                    f'Attempt {attempt + 1} of {max_retries} failed: {e}')
                self.connection = None
                sleep(retry_interval)
        raise CacheOperationException(f'Could not connect to Redis after {
                                      max_retries} attempts.')

    def execute_redis_operation(self, operation, *args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except (redis.ConnectionError, redis.TimeoutError):
            self._init_connection()
            return operation(*args, **kwargs)

    def set(self, key, value=1, ttl=None):
        try:
            self.execute_redis_operation(
                self.connection.set, name=key, value=value, ex=ttl)
        except Exception as e:
            raise CacheOperationException(f'Error setting key {key}: {e}')

    def get(self, key):
        try:
            return self.execute_redis_operation(self.connection.get, name=key)
        except Exception as e:
            raise CacheOperationException(f'Error getting key {key}: {e}')

    def exists(self, key):
        try:
            return self.execute_redis_operation(self.connection.exists, name=key)
        except Exception as e:
            raise CacheOperationException(f'Error checking key {key}: {e}')

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
