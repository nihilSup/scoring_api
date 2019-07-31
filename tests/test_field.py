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
        self.assertEqual(C.val_field.validate(c), ("OK", True))

    def test_valid_validator(self):
        class C(object):
            val_field = field.ValidatedField([self.validate_int])
        c = C()
        c.val_field = 5
        self.assertEqual(c.val_field, 5)
        self.assertEqual(C.val_field.validate(c), ("OK", True))

    def test_validator_error(self):
        class C(object):
            val_field = field.ValidatedField([self.validate_int])
        c = C()
        c.val_field = '5'
        self.assertEqual(c.val_field, '5')
        self.assertEqual(C.val_field.validate(c), ("Must be int", False))


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
        self.assertEqual(C.val_field.validate(c), ("OK", True))

    def test_none_value_in_not_nullable(self):
        class C(object):
            val_field = field.NullableField(nullable=False,
                                            validators=[self.validate_int])
        c = C()
        c.val_field = None
        self.assertIsNone(c.val_field)
        self.assertEqual(C.val_field.validate(c),
                         ("None value in not nullable field", False))

    def test_regular_value(self):
        class C(object):
            val_field = field.NullableField(nullable=False,
                                            validators=[self.validate_int])
        c = C()
        c.val_field = '5'
        self.assertEqual(c.val_field, '5')
        self.assertEqual(C.val_field.validate(c), ("Must be int", False))


class TestRequiredField(unittest.TestCase):
    def setUp(self):
        def validate_int(val):
            if not isinstance(val, int):
                raise ValueError("Must be int")
            return True
        self.validate_int = validate_int

    def test_empty_and_required(self):
        class C(object):
            val_field = field.RequiredField(required=True,
                                            validators=[self.validate_int])
        c = C()
        self.assertEqual(C.val_field.validate(c),
                         ("Missing required field", False))

    def test_empty_and_not_req(self):
        class C(object):
            val_field = field.RequiredField(required=False,
                                            validators=[self.validate_int])
        c = C()
        self.assertEqual(C.val_field.validate(c),
                         ("OK", True))

    def test_val_and_req(self):
        class C(object):
            val_field = field.RequiredField(required=False,
                                            validators=[self.validate_int])
        c = C()
        c.val_field = '5'
        self.assertEqual(c.val_field, '5')
        self.assertEqual(C.val_field.validate(c), ("Must be int", False))


class TestTypedField(unittest.TestCase):
    def test_str_field(self):
        class C(object):
            str_field = field.TypedField(type_=str)
        c = C()
        c.str_field = 'some'
        self.assertEqual(c.str_field, 'some')
        self.assertEqual(C.str_field.validate(c), ("OK", True))

    def test_mixed_field(self):
        class C(object):
            mixed_field = field.TypedField(type_=(list, int))
        c = C()
        c.mixed_field = ['a']
        self.assertEqual(C.mixed_field.validate(c), ("OK", True))
        c.mixed_field = 5
        self.assertEqual(c.mixed_field, 5)
        self.assertEqual(C.mixed_field.validate(c), ("OK", True))

    def test_invalid_str_field(self):
        class C(object):
            str_field = field.TypedField(type_=str)
        c = C()
        c.str_field = 5
        msg, is_valid = C.str_field.validate(c)
        self.assertEqual((is_valid, msg.startswith('Incorrect type')),
                         (False, True))

    def test_invalid_mixed_field(self):
        class C(object):
            mixed_field = field.TypedField(type_=(list, int))
        c = C()
        c.mixed_field = 'some'
        msg, is_valid = C.mixed_field.validate(c)
        self.assertEqual((is_valid, msg.startswith('Incorrect type')),
                         (False, True))


if __name__ == '__main__':
    unittest.main()
