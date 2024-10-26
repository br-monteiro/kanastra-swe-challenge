from abc import ABC, abstractmethod


class CacheClient(ABC):
    @abstractmethod
    def get(self, key):
        pass
    
    @abstractmethod
    def exists(self, key):
        pass

    @abstractmethod
    def set(self, key, value = None, ttl: int = None):
        pass

    @abstractmethod
    def close_connection(self):
        pass
