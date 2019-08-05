import unittest
import functools

from scoring_api import scoring


def cases(cases):
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args):
            for case in cases:
                case = case if isinstance(case, tuple) else (case, )
                f(*args, *case)
        return inner_wrapper
    return wrapper


class TestGetScore(unittest.TestCase):

    def setUp(self):
        class StoreMock(object):

            def __init__(self):
                self.store = {}

            def get(self, key):
                return self.store.get(key, None)

            def cache_get(self, key):
                return self.get(key)

            def cache_set(self, key, val, sec):
                self.store[key] = val

        self.store = StoreMock()

    @cases([
        (('phone', 'email', 'bday', 'g', 'f_name', 'l_name'), 5),
        (('phone', 'email'), 3),
        (('', '', 'bday', 'g', 'f_name', 'l_name'), 2),
    ])
    def test_get_score_basic(self, args, expected):
        self.assertEqual(scoring.get_score(self.store, *args), expected)

    def test_get_score_cached(self):
        args = ('phone1', 'email1')
        self.store.cache_set(scoring._score_key(*args), -1, 5)
        self.assertEqual(scoring.get_score(self.store, *args), -1)

    def test_get_score_missed_cached(self):
        args = ('phone1', 'email1')
        self.store.cache_set(scoring._score_key(*args), None, 5)
        self.assertEqual(scoring.get_score(self.store, *args), 3)

    def test_clients_interests(self):
        cid = 42
        self.store.cache_set("i:%s" % cid, '["aa", "bb"]', 5)
        self.assertEqual(scoring.get_interests(self.store, cid), ['aa', 'bb'])


if __name__ == '__main__':
    unittest.main()
