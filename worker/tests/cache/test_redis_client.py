import pytest
import redis
from unittest.mock import patch, MagicMock
from src.cache.redis_client import RedisClient
from src.cache.exceptions.cache_operation_exception import CacheOperationException


@pytest.fixture
def settings():
    _settings = MagicMock()
    _settings.redis_host = 'host'
    _settings.redis_port = 1234
    _settings.redis_db = 0
    _settings.redis_connection_max_retries = 3
    _settings.redis_connection_retry_interval = 1
    _settings.redis_connect_timeout = 5
    _settings.redis_operation_timeout = 5
    return _settings


@pytest.fixture(autouse=True)
def before_each():
    RedisClient._instance = None


@patch('src.cache.redis_client.redis.Redis')
def test_singleton_instance(mock_redis, settings):
    client1 = RedisClient(settings)
    client2 = RedisClient(settings)

    assert client1 is client2
    mock_redis.assert_called_once_with(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        socket_connect_timeout=settings.redis_connect_timeout,
        socket_timeout=settings.redis_operation_timeout
    )


@patch('src.cache.redis_client.redis.Redis')
def test_init_connection_success(mock_redis, settings):
    client = RedisClient(settings)

    client.connection.ping.assert_called_once()
    assert client.connection is not None


@patch('src.cache.redis_client.redis.Redis')
@patch('src.cache.redis_client.sleep')
def test_init_connection_failure(mock_sleep, mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.ping.side_effect = redis.ConnectionError
    mock_redis.return_value = mock_instance

    with pytest.raises(CacheOperationException):
        RedisClient(settings)

    assert mock_instance.ping.call_count == settings.redis_connection_max_retries
    mock_sleep.assert_called_with(settings.redis_connection_retry_interval)


@patch('src.cache.redis_client.redis.Redis')
@patch('src.cache.redis_client.sleep')
def test_init_connection_failure_timeout(mock_sleep, mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.ping.side_effect = redis.TimeoutError
    mock_redis.return_value = mock_instance

    with pytest.raises(CacheOperationException):
        RedisClient(settings)

    assert mock_instance.ping.call_count == settings.redis_connection_max_retries
    mock_sleep.assert_called_with(settings.redis_connection_retry_interval)


@patch('src.cache.redis_client.redis.Redis')
def test_set_value(mock_redis, settings):
    client = RedisClient(settings)
    key = 'test_key'
    value = 'test_value'

    client.set(key, value)

    client.connection.set.assert_called_with(
        name='test_key', value='test_value', ex=None)


@patch('src.cache.redis_client.redis.Redis')
def test_get_value(mock_redis, settings):
    client = RedisClient(settings)
    key = 'test_key'
    value = 'test_value'
    client.connection.get.return_value = value.encode()

    result = client.get(key)

    client.connection.get.assert_called_with(name=key)
    assert result == value.encode()


@patch('src.cache.redis_client.redis.Redis')
def test_exists_key(mock_redis, settings):
    client = RedisClient(settings)
    key = 'test_key'
    exists = 1
    client.connection.exists.return_value = exists

    result = client.exists(key)

    client.connection.exists.assert_called_with(name=key)
    assert result == exists


@patch('src.cache.redis_client.redis.Redis')
def test_set_with_reconnection_by_connection_error(mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.set.side_effect = [redis.ConnectionError, None]
    mock_instance.ping.return_value = True
    mock_redis.return_value = mock_instance

    client = RedisClient(settings)
    client.set('test_key', 'test_value')

    assert mock_instance.set.call_count == 2


@patch('src.cache.redis_client.redis.Redis')
def test_set_with_reconnection_by_timeout_error(mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.set.side_effect = [redis.TimeoutError, None]
    mock_instance.ping.return_value = True
    mock_redis.return_value = mock_instance

    client = RedisClient(settings)
    client.set('test_key', 'test_value')

    assert mock_instance.set.call_count == 2


@patch('src.cache.redis_client.redis.Redis')
def test_set_failure_after_reconnection(mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.ping.return_value = True
    mock_instance.set.side_effect = [redis.ConnectionError, redis.TimeoutError]
    mock_redis.return_value = mock_instance
    client = RedisClient(settings)

    with pytest.raises(CacheOperationException):
        client.set('test_key', 'test_value')

    assert client.connection.set.call_count == 2


@patch('src.cache.redis_client.redis.Redis')
def test_get_with_reconnection_by_connection_error(mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.get.side_effect = [redis.ConnectionError, b'test_value']
    mock_instance.ping.return_value = True
    mock_redis.return_value = mock_instance

    client = RedisClient(settings)
    result = client.get('test_key')

    assert mock_instance.get.call_count == 2
    assert result == b'test_value'


@patch('src.cache.redis_client.redis.Redis')
def test_get_with_reconnection_by_timeout_error(mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.get.side_effect = [redis.TimeoutError, b'test_value']
    mock_instance.ping.return_value = True
    mock_redis.return_value = mock_instance

    client = RedisClient(settings)
    result = client.get('test_key')

    assert mock_instance.get.call_count == 2
    assert result == b'test_value'


@patch('src.cache.redis_client.redis.Redis')
def test_get_failure_after_reconnection(mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.ping.return_value = True
    mock_instance.get.side_effect = [redis.ConnectionError, redis.TimeoutError]
    mock_redis.return_value = mock_instance
    client = RedisClient(settings)

    with pytest.raises(CacheOperationException):
        client.get('test_key')

    assert client.connection.get.call_count == 2


@patch('src.cache.redis_client.redis.Redis')
def test_exists_with_reconnection_by_connection_error(mock_redis, settings):
    exists = 1
    mock_instance = MagicMock()
    mock_instance.exists.side_effect = [redis.ConnectionError, exists]
    mock_instance.ping.return_value = True
    mock_redis.return_value = mock_instance

    client = RedisClient(settings)
    result = client.exists('test_key')

    assert mock_instance.exists.call_count == 2
    assert result == exists


@patch('src.cache.redis_client.redis.Redis')
def test_exists_with_reconnection_by_timeout_error(mock_redis, settings):
    exists = 1
    mock_instance = MagicMock()
    mock_instance.exists.side_effect = [redis.TimeoutError, exists]
    mock_instance.ping.return_value = True
    mock_redis.return_value = mock_instance

    client = RedisClient(settings)
    result = client.exists('test_key')

    assert mock_instance.exists.call_count == 2
    assert result == exists


@patch('src.cache.redis_client.redis.Redis')
def test_exists_failure_after_reconnection(mock_redis, settings):
    mock_instance = MagicMock()
    mock_instance.ping.return_value = True
    mock_instance.exists.side_effect = [
        redis.ConnectionError, redis.TimeoutError]
    mock_redis.return_value = mock_instance
    client = RedisClient(settings)

    with pytest.raises(CacheOperationException):
        client.exists('test_key')

    assert client.connection.exists.call_count == 2


@patch('src.cache.redis_client.redis.Redis')
def test_close_connection(mock_redis, settings):
    mock_instance = MagicMock()
    mock_redis.return_value = mock_instance
    client = RedisClient(settings)

    client.close_connection()

    mock_instance.close.assert_called_once()
    assert client.connection is None
