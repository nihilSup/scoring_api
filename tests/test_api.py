import unittest
import functools

from scoring_api import api


def with_cases(cases):
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args):
            for case in cases:
                f(*args, *case)
        return inner_wrapper
    return wrapper


def help_msg(**kwargs):
    # return "val: {}, expected: {}".format(val, expected)
    return str(kwargs)


class TestCharField(unittest.TestCase):
    @with_cases([
        ('abcde', True),
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


class TestEmailField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            email_field = api.EmailField(required=True, nullable=False)
        self.obj = SomeCls()

    @with_cases([
        ('ab@cde', True),
        ('abcde', False),
        (None, False),
        (5, False)
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
    @with_cases([
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


class TestRequest(unittest.TestCase):
    @with_cases([
        (dict(char_field='aaaa', phone_field=12345), api.OK),
        (dict(char_field='', phone_field=12345, opt_char_field='a'), api.OK),
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

    @with_cases([
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

if __name__ == '__main__':
    unittest.main()
