

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


class BaseField(Field):
    def __init__(self, required, nullable, **kwargs):
        self.required = required
        self.nullable = nullable
        self.val_set_flag = False
        super().__init__(**kwargs)

    def __set__(self, obj, val):
        if not self.nullable and val is None:
            raise ValueError("Value is required, can't be None")
        self.val_set_flag = True
        super().__set__(obj, val)

    def __get__(self, obj, owner):
        if self.required and not self.val_set_flag:
            raise ValueError("Value has been not set, but it is required")
        return super().__get__(obj, owner)


class TypedField(Field):
    """Class based equivalent of check_type validator"""
    def __init__(self, type_, **kwargs):
        self.type = type_
        super().__init__(**kwargs)

    def __set__(self, obj, val):
        if isinstance(val, tuple(self.type)):
            super().__set__(obj, val)
        else:
            raise TypeError('value must be instance of any of {}'
                            .format(str(self.type)))


class ValidatedField(Field):
    """Field descriptor with set validators"""
    def __init__(self, validators=None, **kwargs):
        """Args:
            validators: list of callable"""
        if not validators:
            validators = []
        self.validators = validators
        super().__init__(**kwargs)

    def __set__(self, obj, val):
        for validator in self.validators:
            validator(val)
        super().__set__(obj, val)
