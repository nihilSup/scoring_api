import unittest

from scoring_api import field


class TestField(unittest.TestCase):
    def test_default_name(self):
        class SomeCls():
            my_field = field.Field()
        sc = SomeCls()
        sc.my_field = 5
        self.assertTrue('_my_field' in sc.__dict__)
        self.assertTrue(sc.my_field == 5)


class TestBaseField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            req_null_field = field.BaseField(required=True, nullable=True,
                                             default=-1)
            not_req_not_null_field = field.BaseField(required=False,
                                                     nullable=False)
            req_not_null_field = field.BaseField(required=True, nullable=False)
            not_req_null_field = field.BaseField(required=False, nullable=True)
        self.obj = SomeCls()

    def test_valid_cases(self):
        with self.assertRaises(ValueError):
            _ = self.obj.req_null_field
        self.obj.req_null_field = None
        _ = self.obj.req_null_field

    def test_invalid_cases(self):
        _ = self.obj.not_req_not_null_field
        with self.assertRaises(ValueError):
            self.obj.not_req_not_null_field = None


class TestTypedField(unittest.TestCase):
    def setUp(self):
        class SomeCls(object):
            str_field = field.TypedField(type_=[str])
            mixed_field = field.TypedField(type_=[list, int])
        self.obj = SomeCls()

    def test_valid(self):
        self.obj.str_field = 'some'
        self.assertEqual(self.obj.str_field, 'some')
        self.obj.mixed_field = ['a']
        self.obj.mixed_field = 5
        self.assertEqual(self.obj.mixed_field, 5)

    def test_invalid(self):
        with self.assertRaises(TypeError):
            self.obj.str_field = 5
        with self.assertRaises(TypeError):
            self.obj.mixed_field = 'some'


class TestTypedField(unittest.TestCase):
    def setUp(self):
        def validate_len(val):
            if len(str(val)) != 3:
                raise ValueError('incorrect length')

        class SomeCls(object):
            len_field = field.ValidatedField(validators=[
                validate_len,
                validate_len
            ])
        self.obj = SomeCls()

    def test_typed_field(self):
        self.obj.len_field = 111
        self.obj.len_field = 'abc'
        with self.assertRaises(ValueError):
            self.obj.len_field = None
        with self.assertRaises(ValueError):
            self.obj.len_field = 1
        with self.assertRaises(ValueError):
            self.obj.len_field = 'a'
        with self.assertRaises(ValueError):
            self.obj.len_field = 'abcd'


if __name__ == '__main__':
    unittest.main()
