import unittest
import functools

from scoring_api import api
from tests.utils import cases


class TestCharField(unittest.TestCase):
    @cases([
        'abcde',
        'a',
        '1',
    ])
    def test_basic_func_valid(self, val):
        class C(object):
            char_field = api.CharField(required=True, nullable=False)
        c = C()
        c.char_field = val
        self.assertEqual(c.char_field, val)
        C.char_field.validate(c)

    @cases([
        '',
        None,
        5
    ])
    def test_basic_func_invalid(self, val):
        class C(object):
            char_field = api.CharField(required=True, nullable=False)
        c = C()
        c.char_field = val
        self.assertEqual(c.char_field, val)
        with self.assertRaises((TypeError, ValueError)):
            C.char_field.validate(c)


class TestArgumentsField(unittest.TestCase):
    @cases([
        {'a': 1},
    ])
    def test_basic_func_valid(self, val):
        class C(object):
            field = api.ArgumentsField(required=True, nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        C.field.validate(c)

    @cases([
        {},
        None,
    ])
    def test_basic_func_invalid(self, val):
        class C(object):
            field = api.ArgumentsField(required=True, nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        with self.assertRaises(ValueError):
            C.field.validate(c)


class TestEmailField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            email_field = api.EmailField(required=True, nullable=False)
        self.obj = SomeCls()

    @cases([
        'ab@cde',
    ])
    def test_valid_cases_valid(self, val):
        class C(object):
            email_field = api.EmailField(required=True, nullable=False)
        c = C()
        c.email_field = val
        self.assertEqual(c.email_field, val)
        C.email_field.validate(c)

    @cases([
        'abcde',
        None,
        5,
        '',
    ])
    def test_valid_cases_invalid(self, val):
        class C(object):
            email_field = api.EmailField(required=True, nullable=False)
        c = C()
        c.email_field = val
        self.assertEqual(c.email_field, val)
        with self.assertRaises((TypeError, ValueError)):
            C.email_field.validate(c)


class TestPhoneField(unittest.TestCase):
    @cases([
        '71234567890',
        71234567890,
    ])
    def test_valid_cases(self, val):
        class C(object):
            field = api.PhoneField(length=11, prefix='7', required=True,
                                   nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        C.field.validate(c)

    @cases([
            'abcde', None, '12345678901', 12345678901,
            '123456789012', 123456789012,
        ])
    def test_valid_cases(self, val):
        class C(object):
            field = api.PhoneField(length=11, prefix='7', required=True,
                                   nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        with self.assertRaises((TypeError, ValueError)):
            C.field.validate(c)


class TestDateField(unittest.TestCase):
    @cases([
        '14.04.1989',
    ])
    def test_date_field_basic(self, val):
        class C(object):
            field = api.DateField(fmt='%d.%m.%Y', required=True,
                                  nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        C.field.validate(c)

    @cases([
        '144.04.1989',
        14.04,
        -1,
        None,
    ])
    def test_date_field_basic_invalid(self, val):
        class C(object):
            field = api.DateField(fmt='%d.%m.%Y', required=True,
                                  nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        with self.assertRaises((ValueError, TypeError)):
            C.field.validate(c)

    @cases([
        -1,
        None,
    ])
    def test_invalid_format(self, fmt):
        with self.assertRaises(ValueError):
            class C(object):
                field = api.DateField(fmt=fmt, required=True,
                                      nullable=False)

    @cases([
        ('-1', '14.04.1989'),
        ('-1', '-2'),
    ])
    def test_failed_fmt(self, fmt, val):
        class C(object):
            field = api.DateField(fmt=fmt, required=True,
                                  nullable=False)
        c = C()
        c.field = val
        with self.assertRaises(ValueError):
            C.field.validate(c)


class TestBirthDayField(unittest.TestCase):
    @cases([
        '14.04.1989',
        '09.01.1992',
    ])
    def test_birthdayfield_valid(self, val):
        class C(object):
            field = api.BirthDayField(years=70, fmt='%d.%m.%Y', required=True,
                                      nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        C.field.validate(c)

    @cases([
        '01.01.0001',
        '',
        None,
    ])
    def test_birthdayfield_valid(self, val):
        class C(object):
            field = api.BirthDayField(years=70, fmt='%d.%m.%Y', required=True,
                                      nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        with self.assertRaises((ValueError, TypeError)):
            C.field.validate(c)

    @cases([-1, 0, None, '0', '-1'])
    def test_bad_years(self, years):
        with self.assertRaises((ValueError, TypeError)):
            class C(object):
                field = api.BirthDayField(years=years, fmt='%d.%m.%Y',
                                          required=True, nullable=False)


class TestGenderField(unittest.TestCase):
    @cases([
        2, 1, 0
    ])
    def test_table_tests(self, val):
        class C(object):
            field = api.GenderField(range_=[0, 1, 2], required=True,
                                    nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        C.field.validate(c)

    @cases([
        -1, '1', [1, 2], None, [], [1, '2', 3], [1, '', 3]
    ])
    def test_table_tests_invalid(self, val):
        class C(object):
            field = api.GenderField(range_=[0, 1, 2], required=True,
                                    nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        with self.assertRaises((ValueError, TypeError)):
            C.field.validate(c)


class TestClientIDsField(unittest.TestCase):
    @cases([
        [1, 2],
    ])
    def test_table_tests(self, val):
        class C(object):
            field = api.ClientIDsField(required=True, nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        C.field.validate(c)

    @cases([
        [], [[]], None, 'abcde', ['1', '2'], [[1], [2]],
    ])
    def test_table_tests_invalid(self, val):
        class C(object):
            field = api.ClientIDsField(required=True, nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        with self.assertRaises((ValueError, TypeError)):
            C.field.validate(c)


class TestRequest(unittest.TestCase):
    @cases([
        dict(char_field='aaaa', phone_field=12345),
    ])
    def test_basic_cases(self, request):
        class C(api.Request):
            char_field = api.CharField(required=True, nullable=False)
            phone_field = api.PhoneField(required=True, nullable=True,
                                         length=5, prefix=1)
            opt_char_field = api.CharField(required=False, nullable=False)

            def validate(self):
                return super().validate()
        c = C(request)
        c.validate()

    @cases([
        dict(char_field='', phone_field=12345, opt_char_field='a'),
        dict(char_field=1, phone_field=22345, opt_char_field='a'),
        dict(phone_field=12345, opt_char_field='a'),
        dict(),
        dict(char_field='', phone_field=-1),
    ])
    def test_basic_cases_invalid(self, request):
        class C(api.Request):
            char_field = api.CharField(required=True, nullable=False)
            phone_field = api.PhoneField(required=True, nullable=True,
                                         length=5, prefix=1)
            opt_char_field = api.CharField(required=False, nullable=False)

            def validate(self):
                return super().validate()
        c = C(request)
        with self.assertRaises(Exception):
            c.validate()

    @cases([
        {},
        dict(char_field='aaaa', phone_field=12345),
    ])
    def test_all_opt(self, request):
        class C(api.Request):
            char_field = api.CharField(required=False, nullable=False)
            phone_field = api.PhoneField(required=False, nullable=True,
                                         length=5, prefix=1)
            opt_char_field = api.CharField(required=False, nullable=False)

            def validate(self):
                return super().validate()
        c = C(request)
        c.validate()

    @cases([
        dict(char_field='', phone_field=-1),
    ])
    def test_all_opt_invalid(self, request):
        class C(api.Request):
            char_field = api.CharField(required=False, nullable=False)
            phone_field = api.PhoneField(required=False, nullable=True,
                                         length=5, prefix=1)
            opt_char_field = api.CharField(required=False, nullable=False)

            def validate(self):
                return super().validate()
        c = C(request)
        with self.assertRaises(Exception):
            c.validate()


class TestRequestsSuite(unittest.TestCase):
    @cases([
        {"account": "foo", "login": "bar", "method": "some", "token": "",
         "arguments": {}},
        {"login": "bar", "method": "some", "token": "",
         "arguments": {}},
        {"login": "", "method": "a", "token": "",
         "arguments": {}},
        {"login": None, "method": "a", "token": None,
         "arguments": None},
    ])
    def test_method_request(self, request):
        meth_req_obj = api.MethodRequest(request)
        meth_req_obj.validate()

    @cases([
        {},
        {"method": "some", "token": "",
         "arguments": {}},
        {"login": None, "method": "a", "token": 1,
         "arguments": None},
    ])
    def test_method_request_invalid(self, request):
        meth_req_obj = api.MethodRequest(request)
        with self.assertRaises(Exception):
            meth_req_obj.validate()

    @cases([
        {"phone": "77asdfghjkl", "email": "bb@aa"},
    ])
    def test_online_score_request(self, request):
        req_obj = api.OnlineScoreRequest(request)
        req_obj.validate()

    @cases([
        {"phone": "qdads", "email": "bb@aa", "gender": 0,
         "birthday": "01.01.2001", "first_name": "s", "last_name": 2},
        {"phone": "qdads", "gender": 0, "first_name": "s"},
        {},
    ])
    def test_online_score_request_invalid(self, request):
        req_obj = api.OnlineScoreRequest(request)
        with self.assertRaises(Exception):
            req_obj.validate()

    @cases([
        {"phone": "qdads", "email": "bb@aa", "gender": 0,
         "birthday": "01.01.2001", "first_name": "s", "last_name": 2},
        {},
        {'phone': '', "email": ''}
    ])
    def test_has(self, request):
        req_obj = api.OnlineScoreRequest(request)
        self.assertEqual(sorted(req_obj.has), sorted(request.keys()))

    @cases([
        {"client_ids": [1]},
        {"client_ids": [1, 2]},
    ])
    def test_clients_interests_req(self, request):
        req_obj = api.ClientsInterestsRequest(request)
        req_obj.validate()

    @cases([
        {},
        {"client_ids": []},
        {"client_ids": ['1', '1']},
    ])
    def test_clients_interests_req_invalid(self, request):
        req_obj = api.ClientsInterestsRequest(request)
        with self.assertRaises(Exception):
            req_obj.validate()

    @cases([
        [1, 2, 3],
        [1],
    ])
    def test_nclients(self, ids):
        request = {"client_ids": ids}
        req_obj = api.ClientsInterestsRequest(request)
        self.assertEqual(req_obj.nclients, len(ids))


if __name__ == '__main__':
    unittest.main()
