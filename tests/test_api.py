import unittest

from scoring_api import api


class TestCharField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            char_field = api.CharField(required=True, nullable=False)
        self.obj = SomeCls()

    def test_valid_cases(self):
        self.obj.char_field = 'abcde'
        self.assertEqual(self.obj.char_field, 'abcde')
        with self.assertRaises(ValueError):
            self.obj.char_field = None
        with self.assertRaises(TypeError):
            self.obj.char_field = 5


class TestEmailField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            email_field = api.EmailField(required=True, nullable=False)
        self.obj = SomeCls()

    def test_valid_cases(self):
        self.obj.email_field = 'ab@cde'
        self.assertEqual(self.obj.email_field, 'ab@cde')
        with self.assertRaises(ValueError):
            self.obj.email_field = 'abcde'
        with self.assertRaises(ValueError):
            self.obj.email_field = None
        with self.assertRaises(TypeError):
            self.obj.email_field = 5


class TestPhoneField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            field = api.PhoneField(length=11, prefix='7', required=True,
                                   nullable=False)
        self.obj = SomeCls()

    def test_valid_cases(self):
        self.obj.field = '71234567890'
        self.obj.field = 71234567890
        self.assertEqual(self.obj.field, 71234567890)

    def test_invalid_cases(self):
        cases = ['abcde', None, '12345678901', 12345678901, '123456789012',
                 123456789012]
        for val in cases:
            with self.assertRaises(ValueError):
                self.obj.field = val


if __name__ == '__main__':
    unittest.main()
