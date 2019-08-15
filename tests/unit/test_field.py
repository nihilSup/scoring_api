import unittest

from scoring_api import field


class TestField(unittest.TestCase):
    def test_basic_func(self):
        class SomeCls():
            my_field = field.Field()
        sc = SomeCls()
        sc.my_field = 5
        self.assertTrue('_my_field' in sc.__dict__)
        self.assertTrue(sc.my_field == 5)


class TestValidatedField(unittest.TestCase):
    def setUp(self):
        def validate_int(val):
            if not isinstance(val, int):
                raise ValueError("Must be int")
            return True
        self.validate_int = validate_int

    def test_empty_validator(self):
        class C(object):
            val_field = field.ValidatedField()
        c = C()
        c.val_field = 5
        self.assertEqual(c.val_field, 5)
        C.val_field.validate(c)

    def test_valid_validator(self):
        class C(object):
            val_field = field.ValidatedField([self.validate_int])
        c = C()
        c.val_field = 5
        self.assertEqual(c.val_field, 5)
        C.val_field.validate(c)

    def test_validator_error(self):
        class C(object):
            val_field = field.ValidatedField([self.validate_int])
        c = C()
        c.val_field = '5'
        self.assertEqual(c.val_field, '5')
        with self.assertRaises(ValueError):
            C.val_field.validate(c)


class TestNullableField(unittest.TestCase):
    def setUp(self):
        def validate_int(val):
            if not isinstance(val, int):
                raise ValueError("Must be int")
            return True
        self.validate_int = validate_int

    def test_none_value_in_nullable(self):
        class C(object):
            val_field = field.NullableField(nullable=True,
                                            validators=[self.validate_int])
        c = C()
        c.val_field = None
        self.assertIsNone(c.val_field)
        C.val_field.validate(c)

    def test_none_value_in_not_nullable(self):
        class C(object):
            val_field = field.NullableField(nullable=False,
                                            validators=[self.validate_int])
        c = C()
        c.val_field = None
        self.assertIsNone(c.val_field)
        with self.assertRaises(ValueError):
            C.val_field.validate(c)

    def test_regular_value(self):
        class C(object):
            val_field = field.NullableField(nullable=False,
                                            validators=[self.validate_int])
        c = C()
        c.val_field = '5'
        self.assertEqual(c.val_field, '5')
        with self.assertRaises(ValueError):
            C.val_field.validate(c)


class TestRequiredField(unittest.TestCase):
    def setUp(self):
        def validate_int(val):
            if not isinstance(val, int):
                raise TypeError("Must be int")
            return True
        self.validate_int = validate_int

    def test_empty_and_required(self):
        class C(object):
            val_field = field.RequiredField(required=True,
                                            validators=[self.validate_int])
        c = C()
        with self.assertRaises(ValueError):
            C.val_field.validate(c)

    def test_empty_and_not_req(self):
        class C(object):
            val_field = field.RequiredField(required=False,
                                            validators=[self.validate_int])
        c = C()
        C.val_field.validate(c)

    def test_val_and_req(self):
        class C(object):
            val_field = field.RequiredField(required=False,
                                            validators=[self.validate_int])
        c = C()
        c.val_field = '5'
        self.assertEqual(c.val_field, '5')
        with self.assertRaises(TypeError):
            C.val_field.validate(c)


class TestTypedField(unittest.TestCase):
    def test_str_field(self):
        class C(object):
            str_field = field.TypedField(type_=str)
        c = C()
        c.str_field = 'some'
        self.assertEqual(c.str_field, 'some')
        C.str_field.validate(c)

    def test_mixed_field(self):
        class C(object):
            mixed_field = field.TypedField(type_=(list, int))
        c = C()
        c.mixed_field = ['a']
        C.mixed_field.validate(c)
        c.mixed_field = 5
        self.assertEqual(c.mixed_field, 5)
        C.mixed_field.validate(c)

    def test_invalid_str_field(self):
        class C(object):
            str_field = field.TypedField(type_=str)
        c = C()
        c.str_field = 5
        with self.assertRaises(TypeError):
            C.str_field.validate(c)

    def test_invalid_mixed_field(self):
        class C(object):
            mixed_field = field.TypedField(type_=(list, int))
        c = C()
        c.mixed_field = 'some'
        with self.assertRaises(TypeError):
            C.mixed_field.validate(c)


if __name__ == '__main__':
    unittest.main()
