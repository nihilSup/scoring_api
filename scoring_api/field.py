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
        for validator in self.validators:
            validator(val)
        return None


class NullableField(ValidatedField):
    def __init__(self, nullable, **kwargs):
        self.nullable = nullable
        super().__init__(**kwargs)

    def validate(self, obj):
        val = getattr(obj, self.name, self.default)
        if self.nullable and not val:
            return
        elif not self.nullable and not val and val != 0:
            raise ValueError("None value in not nullable field")
        else:
            super().validate(obj)


class RequiredField(ValidatedField):
    """
    This field must be before NullableField in local precedence order
    """
    def __init__(self, required, **kwargs):
        self.required = required
        super().__init__(**kwargs)

    def validate(self, obj):
        if not hasattr(obj, self.name) and self.required:
            raise ValueError("Missing required field")
        elif not hasattr(obj, self.name) and not self.required:
            return
        else:
            super().validate(obj)


class TypedField(ValidatedField):
    """Class based equivalent of check_type validator"""
    def __init__(self, type_, **kwargs):
        self.type_ = type_
        super().__init__(**kwargs)

    def validate(self, obj):
        val = getattr(obj, self.name, self.default)
        if not isinstance(val, self.type_):
            raise TypeError("Incorrect type, expected any of %s"
                            % str(self.type_))
        else:
            super().validate(obj)
