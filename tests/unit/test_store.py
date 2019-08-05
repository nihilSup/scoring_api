import unittest
import time
import threading

import fakeredis

from scoring_api import store


class TestStore(unittest.TestCase):

    def setUp(self):
        self.server = fakeredis.FakeServer()
        self.redis_mock = fakeredis.FakeStrictRedis(server=self.server)
        self.store = store.RedisStore(
            attempts=2, timeout=1, client_builder=lambda: self.redis_mock
        )

    def test_get_missed_key(self):
        self.assertIsNone(self.store.get('some'))

    def test_get_stored_key(self):
        self.redis_mock.set('name1', 'val1')
        self.assertEqual(self.store.get('name1'), b'val1')

    def test_cached_get(self):
        self.assertIsNone(self.store.cache_get('some'))

    def test_cached_get_missed(self):
        self.redis_mock.set('name1', 'val1')
        self.assertEqual(self.store.cache_get('name1'), b'val1')

    def test_cached_set(self):
        self.store.cache_set('name1', 'val1', 60)
        self.assertEqual(self.store.cache_get('name1'), b'val1')

    def test_cached_set_expired(self):
        self.store.cache_set('name1', 'val1', 1)
        time.sleep(1.5)
        self.assertEqual(self.store.cache_get('name1'), None)

    def test_get_failed_conn(self):
        self.server.connected = False
        with self.assertRaises(Exception):
            self.store.get('bla')

    def test_cache_get_failed_conn(self):
        self.server.connected = False
        self.assertIsNone(self.store.cache_get('bla'))

    def test_cache_set_failed_conn(self):
        self.server.connected = False
        self.store.cache_set('bla', 'blabla', 60)
        self.assertIsNone(self.store.cache_get('bla'))

    def test_reconnect(self):
        self.server.connected = False

        def restore_connection():
            time.sleep(0.5)
            self.server.connected = True

        t = threading.Thread(target=restore_connection)
        t.start()
        self.assertIsNone(self.store.get('bla'))
        t.join()

if __name__ == '__main__':
    unittest.main()
