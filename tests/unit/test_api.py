import unittest
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


def help_msg(**kwargs):
    # return "val: {}, expected: {}".format(val, expected)
    return str(kwargs)


class TestCharField(unittest.TestCase):
    @cases([
        ('abcde', True),
        ('', False),
        ('a', True),
        ('1', True),
        (None, False),
        (5, False),
    ])
    def test_basic_func(self, val, expected):
        # help_str = "val: {}, expected: {}".format(val, expected)

        class C(object):
            char_field = api.CharField(required=True, nullable=False)
        c = C()
        c.char_field = val
        self.assertEqual(c.char_field, val)
        msg, is_valid = C.char_field.validate(c)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))


class TestArgumentsField(unittest.TestCase):
    @cases([
        ({}, False),
        ({'a': 1}, True),
        (None, False),
    ])
    def test_basic_func(self, val, expected):
        class C(object):
            field = api.ArgumentsField(required=True, nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        msg, is_valid = C.field.validate(c)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))


class TestEmailField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            email_field = api.EmailField(required=True, nullable=False)
        self.obj = SomeCls()

    @cases([
        ('ab@cde', True),
        ('abcde', False),
        (None, False),
        (5, False),
        ('', False),
    ])
    def test_valid_cases(self, val, expected):
        class C(object):
            email_field = api.EmailField(required=True, nullable=False)
        c = C()
        c.email_field = val
        self.assertEqual(c.email_field, val)
        msg, is_valid = C.email_field.validate(c)
        # help_str = "val: {}, expected: {}".format(val, expected)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))


class TestPhoneField(unittest.TestCase):
    @cases([
        ('71234567890', True), (71234567890, True), ('abcde', False),
        (None, False), ('12345678901', False), (12345678901, False),
        ('123456789012', False), (123456789012, False),
    ])
    def test_valid_cases(self, val, expected):
        class C(object):
            field = api.PhoneField(length=11, prefix='7', required=True,
                                   nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        msg, is_valid = C.field.validate(c)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))


class TestDateField(unittest.TestCase):
    @cases([
        ('14.04.1989', True),
        ('144.04.1989', False),
        (14.04, False),
        (-1, False),
        (None, False),
    ])
    def test_date_field_basic(self, val, expected):
        class C(object):
            field = api.DateField(fmt='%d.%m.%Y', required=True,
                                  nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        msg, is_valid = C.field.validate(c)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))

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
        msg, is_valid = C.field.validate(c)
        self.assertEqual(is_valid, False, help_msg(val=val, exp=False,
                                                   msg=msg))


class TestBirthDayField(unittest.TestCase):
    @cases([
        ('14.04.1989', True),
        ('09.01.1992', True),
        ('01.01.0001', False),
        ('', False),
        (None, False),
    ])
    def test_birthdayfield(self, val, expected):
        class C(object):
            field = api.BirthDayField(years=70, fmt='%d.%m.%Y', required=True,
                                      nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        msg, is_valid = C.field.validate(c)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))

    @cases([-1, 0, None, '0', '-1'])
    def test_bad_years(self, years):
        with self.assertRaises((ValueError, TypeError)):
            class C(object):
                field = api.BirthDayField(years=years, fmt='%d.%m.%Y',
                                          required=True, nullable=False)


class TestGenderField(unittest.TestCase):
    @cases([
        (2, True),
        (1, True),
        (0, True),
        (-1, False),
        ('1', False),
        ([1, 2], False),
        (None, False),
        ([], False),
        ([1, '2', 3], False),
        ([1, '', 3], False),
    ])
    def test_table_tests(self, val, expected):
        class C(object):
            field = api.GenderField(range_=[0, 1, 2], required=True,
                                    nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        msg, is_valid = C.field.validate(c)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))


class TestClientIDsField(unittest.TestCase):
    @cases([
        ([], False),
        ([[]], False),
        (None, False),
        ('abcde', False),
        ([1, 2], True),
        (['1', '2'], False),
        ([[1], [2]], False),
    ])
    def test_table_tests(self, val, expected):
        class C(object):
            field = api.ClientIDsField(required=True, nullable=False)
        c = C()
        c.field = val
        self.assertEqual(c.field, val)
        msg, is_valid = C.field.validate(c)
        self.assertEqual(is_valid, expected, help_msg(val=val, exp=expected,
                                                      msg=msg))


class TestRequest(unittest.TestCase):
    @cases([
        (dict(char_field='aaaa', phone_field=12345), api.OK),
        (dict(char_field='', phone_field=12345, opt_char_field='a'),
         api.INVALID_REQUEST),
        (dict(char_field=1, phone_field=22345, opt_char_field='a'),
         api.INVALID_REQUEST),
        (dict(phone_field=12345, opt_char_field='a'), api.INVALID_REQUEST),
        (dict(), api.INVALID_REQUEST),
        (dict(char_field='', phone_field=-1), api.INVALID_REQUEST),
    ])
    def test_basic_cases(self, request, expected):
        class C(api.Request):
            char_field = api.CharField(required=True, nullable=False)
            phone_field = api.PhoneField(required=True, nullable=True,
                                         length=5, prefix=1)
            opt_char_field = api.CharField(required=False, nullable=False)

            def validate(self):
                return super().validate()
        c = C(request)
        msg, is_valid = c.validate()
        self.assertEqual(is_valid, expected, help_msg(**request))

    @cases([
        ({}, api.OK),
        (dict(char_field='aaaa', phone_field=12345), api.OK),
        (dict(char_field='', phone_field=-1), api.INVALID_REQUEST),
    ])
    def test_all_opt(self, request, expected):
        class C(api.Request):
            char_field = api.CharField(required=False, nullable=False)
            phone_field = api.PhoneField(required=False, nullable=True,
                                         length=5, prefix=1)
            opt_char_field = api.CharField(required=False, nullable=False)

            def validate(self):
                return super().validate()
        c = C(request)
        msg, valid = c.validate()
        self.assertEqual(valid, expected, msg)


class TestRequestsSuite(unittest.TestCase):
    @cases([
        ({}, api.INVALID_REQUEST),
        ({"account": "foo", "login": "bar", "method": "some", "token": "",
         "arguments": {}}, api.OK),
        ({"login": "bar", "method": "some", "token": "",
         "arguments": {}}, api.OK),
        ({"method": "some", "token": "",
         "arguments": {}}, api.INVALID_REQUEST),
        ({"login": "", "method": "a", "token": "",
         "arguments": {}}, api.OK),
        ({"login": None, "method": "a", "token": None,
         "arguments": None}, api.OK),
        ({"login": None, "method": "a", "token": 1,
         "arguments": None}, api.INVALID_REQUEST),
    ])
    def test_method_request(self, request, expected):
        meth_req_obj = api.MethodRequest(request)
        msg, valid = meth_req_obj.validate()
        self.assertEqual(valid, expected, help_msg(exp=expected, **request))

    @cases([
        ({"phone": "qdads", "email": "bb@aa", "gender": 0,
         "birthday": "01.01.2001", "first_name": "s", "last_name": 2},
         api.INVALID_REQUEST),
        ({"phone": "qdads", "gender": 0, "first_name": "s"},
         api.INVALID_REQUEST),
        ({}, api.INVALID_REQUEST),
        ({"phone": "77asdfghjkl", "email": "bb@aa"},
         api.OK),
    ])
    def test_online_score_request(self, request, expected):
        req_obj = api.OnlineScoreRequest(request)
        msg, valid = req_obj.validate()
        self.assertEqual(valid, expected, help_msg(exp=expected, **request))

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
        ({}, api.INVALID_REQUEST),
        ({"client_ids": []}, api.INVALID_REQUEST),
        ({"client_ids": ['1', '1']}, api.INVALID_REQUEST),
        ({"client_ids": [1]}, api.OK),
        ({"client_ids": [1, 2]}, api.OK),
    ])
    def test_clients_interests_req(self, request, expected):
        req_obj = api.ClientsInterestsRequest(request)
        msg, valid = req_obj.validate()
        self.assertEqual(valid, expected, help_msg(exp=expected, **request))

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
