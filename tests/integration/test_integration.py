import unittest
import threading
from http.server import HTTPServer
import requests
import functools

from scoring_api import api


def cases(cases):
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args):
            for case in cases:
                case = case if isinstance(case, tuple) else (case, )
                f(*args, *case)
        return inner_wrapper
    return wrapper


class TestApp(unittest.TestCase):
    def setUp(self):
        self.host = 'localhost'
        self.port = 8080
        server = HTTPServer((self.host, self.port), api.MainHTTPHandler)
        self.server = server
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()

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
        self.assertTrue(response.status_code == api.OK, response.status_code)

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
        ({"account": "horns&hoofs", "login": "admin", "method":
         "online_score", "arguments":
            {}}, api.INVALID_REQUEST),
    ])
    def test_handler_online_score(self, json, expected):
        json['token'] = api.digestize(api.MethodRequest(json))
        response = requests.post(self.url, json=json)
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
        self.assertTrue(response.status_code == expected, response.status_code)


if __name__ == '__main__':
    unittest.main()
