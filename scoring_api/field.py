"""Descriptor field module"""


class Field(object):
    """Basic descriptor field. Attribute value is stored in manager class.
    Stored attribute's name is constructed or can be provided by calling
    __set_name__ method"""
    __count = 0

    def __init__(self, default=None):
        self.default = default
        cls = self.__class__
        self.name = '_{}_#{}'.format(cls.__name__, cls.__count)
        cls.__count += 1

    def __get__(self, obj, owner):
        if not obj:
            return self
        return getattr(obj, self.name, self.default)

    def __set__(self, obj, val):
        setattr(obj, self.name, val)

    def __set_name__(self, owner, name):
        self.name = '_' + name


class NamedDescrMeta(type):
    """Metaclass companion for descriptor like object to handle descriptor
    value names in < python 3.6"""
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        for attr_name, attr_val in attrs:
            if isinstance(attr_val, Field):
                attr_val.__set_name__(cls, attr_name)


class ValidatedField(Field):
    """
    Field descriptor with set validators.
    Args:
        validators: list of callable.
    """
    def __init__(self, validators=None, **kwargs):
        """Args:
            validators: list of callable"""
        if not validators:
            validators = []
        self.validators = validators
        super().__init__(**kwargs)

    def validate(self, obj):
        val = getattr(obj, self.name, self.default)
        try:
            res = all(validator(val) for validator in self.validators)
        except (ValueError, TypeError) as e:
            return str(e), False
        return "OK" if res else "Failed", res


class NullableField(ValidatedField):
    def __init__(self, nullable, **kwargs):
        self.nullable = nullable
        super().__init__(**kwargs)

    def validate(self, obj):
        val = getattr(obj, self.name, self.default)
        if self.nullable and not val:
            return "OK", True
        elif not self.nullable and not val and val != 0:
            return "None value in not nullable field", False
        else:
            return super().validate(obj)


class RequiredField(ValidatedField):
    """
    This field must be before NullableField in local precedence order
    """
    def __init__(self, required, **kwargs):
        self.required = required
        super().__init__(**kwargs)

    def validate(self, obj):
        if not hasattr(obj, self.name) and self.required:
            return "Missing required field", False
        elif not hasattr(obj, self.name) and not self.required:
            return "OK", True
        else:
            return super().validate(obj)


class TypedField(ValidatedField):
    """Class based equivalent of check_type validator"""
    def __init__(self, type_, **kwargs):
        self.type_ = type_
        super().__init__(**kwargs)

    def validate(self, obj):
        val = getattr(obj, self.name, self.default)
        if not isinstance(val, self.type_):
            return ("Incorrect type, expected any of %s" % str(self.type_),
                    False)
        else:
            return super().validate(obj)
