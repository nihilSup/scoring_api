import abc
import time

import redis


class Store(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, key):
        pass

    @abc.abstractmethod
    def cache_get(self, key):
        pass

    @abc.abstractmethod
    def cache_set(key, val, sec):
        pass


class RedisStore(Store):

    def __init__(self, host='localhost', port=6379, client_builder=None,
                 attempts=3, timeout=5):
        self.host = host
        self.port = port
        attempts = int(attempts)
        self.attempts = attempts if attempts > 0 else 1
        timeout = int(timeout)
        self.timeout = timeout if timeout > 0 else None
        self.sleep_time = 3
        if not client_builder:
            def def_builder():
                return redis.Redis(host=self.host, port=self.port,
                                   socket_timeout=self.timeout)
            client_builder = def_builder
        self.client_builder = client_builder
        self.client = self.client_builder()

    def _get_client(self):
        attempt = 0
        while True:
            try:
                self.client.ping()
                break
            except redis.ConnectionError:
                if attempt >= self.attempts:
                    raise
                time.sleep(self.sleep_time)
                self.client = self.client_builder()
                attempt += 1
        return self.client

    def get(self, key):
        client = self._get_client()
        return client.get(key)

    def cache_get(self, key):
        try:
            client = self._get_client()
            return client.get(key)
        except redis.RedisError:
            return None

    def cache_set(self, key, val, sec):
        try:
            client = self._get_client()
            client.setex(key, sec, val)
        except redis.RedisError:
            pass
