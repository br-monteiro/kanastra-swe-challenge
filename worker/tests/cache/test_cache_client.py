from src.cache.cache_client import CacheClient


def test_abstract_methods():
    CacheClient.__abstractmethods__ = set()

    class Dummy(CacheClient):
        pass

    d = Dummy()
    assert d.get('key') is None
    assert d.set('key', 'value') is None
    assert d.exists('key') is None
    assert d.close_connection() is None
