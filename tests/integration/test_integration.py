import unittest
import threading
import requests
import functools
import os
from http.server import HTTPServer

import fakeredis

from scoring_api import api, store
from tests.utils import cases


class TestApp(unittest.TestCase):
    def setUp(self):
        self.host = 'localhost'
        self.port = 8080
        if 'REDIS_HOST' in os.environ and 'REDIS_PORT' in os.environ:
            api.MainHTTPHandler.store = store.RedisStore(
                host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'],
                attempts=2, timeout=1)
            server = HTTPServer((self.host, self.port), api.MainHTTPHandler)
            self.server = server
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.setDaemon(True)
            server_thread.start()
        else:
            self.skipTest("There are no redis env vars REDIS_HOST and REDIS_PORT")

    def tearDown(self):
        self.server.server_close()

    @property
    def url(self):
        return 'http://{host}:{port}/method/'.format(host=self.host,
                                                     port=self.port)

    @cases([
        {"account": "horns&hoofs", "login": "admin", "method":
         "clients_interests", "arguments":
            {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}},
        {"account": "horns&hoofs", "login": "some_guy", "method":
         "clients_interests", "arguments":
            {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}},
    ])
    def test_basic(self, json):
        json['token'] = api.digestize(api.MethodRequest(json))
        response = requests.post(self.url, json=json)
        self.assertTrue(response.status_code == api.OK, response.text)

    @cases([
        {"account": "horns&hoofs", "login": "admin", "method":
         "clients_interests", "arguments":
            {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}},
    ])
    def test_handler_invalid_token(self, json):
        json['token'] = '-1'
        response = requests.post(self.url, json=json)
        self.assertTrue(response.status_code == api.FORBIDDEN,
                        response.status_code)

    @cases([
        ({"account": "horns&hoofs", "login": "admin", "method":
         "online_score", "arguments":
            {"phone": "71111111111", "email": "some@some"}}, api.OK),
        ({"account": "horns&hoofs", "login": "dude", "method":
         "online_score", "arguments":
            {"phone": "71111111111", "email": "some@some"}}, api.OK),
        ({"account": "horns&hoofs", "login": "admin", "method":
         "online_score", "arguments":
            {}}, api.INVALID_REQUEST),
    ])
    def test_handler_online_score(self, json, expected):
        json['token'] = api.digestize(api.MethodRequest(json))
        response = requests.post(self.url, json=json)
        if expected == api.OK:
            self.assertIsNotNone(response.json()['response']['score'])
        self.assertTrue(response.status_code == expected, response.status_code)

    @cases([
        ({"account": "horns&hoofs", "login": "admin", "method":
         "clients_interests", "arguments":
            {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}}, api.OK),
        ({"account": "horns&hoofs", "login": "admin", "method":
         "clients_interests", "arguments":
            {}}, api.INVALID_REQUEST),
    ])
    def test_handler_clients_interests(self, json, expected):
        json['token'] = api.digestize(api.MethodRequest(json))
        response = requests.post(self.url, json=json)
        if expected == api.OK:
            self.assertIsNotNone(response.json()['response'])
        self.assertTrue(response.status_code == expected, response.status_code)


if __name__ == '__main__':
    unittest.main()
