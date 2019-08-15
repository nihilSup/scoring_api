import datetime
from dateutil.relativedelta import relativedelta


def has_length(length):
    if length <= 0:
        raise ValueError('Length must be positive int')
    length = int(length)

    def valdiate_length(val):
        cur_length = len(str(val))
        if cur_length != length:
            raise ValueError('Incorrect length. Expected {}, but got {}'
                             .format(length, cur_length))
        else:
            return True
    return valdiate_length


def starts_with(char):
    char = str(char)

    def validate_prefix(val):
        first = str(val)[0]
        if first != char:
            raise ValueError('Incorrect prefix. Expected {}, but got {}'
                             .format(char, first))
        else:
            return True
    return validate_prefix


def check_if_email(val):
    if '@' not in val:
        raise ValueError('There is no @ in email field')
    else:
        return True


def is_date(fmt):
    if not isinstance(fmt, str):
        raise ValueError('Format must be string')

    def valdiate_date(val):
        datetime.datetime.strptime(val, fmt)
        return True

    return valdiate_date


def is_age_le(years, fmt):
    years = int(years)
    if years <= 0:
        raise ValueError('Length must be positive int')

    def validate_age(val):
        bday = datetime.datetime.strptime(val, fmt)
        now = datetime.datetime.now()
        if relativedelta(now, bday).years > years:
            raise ValueError('Age is bigger then {}'.format(years))
        else:
            return True
    return validate_age


def int_in_range(range_):
    def validate_int_in_range(val):
        if val not in range_:
            raise ValueError('Value: {} not in range'.format(val))
        else:
            return True
    return validate_int_in_range


def check_type(type_):
    def validate_type(val):
        if not isinstance(val, type_):
            raise TypeError('value must be instance of any of {}'
                            .format(str(type_)))
        else:
            return True
    return validate_type


def item_has_type(type_):
    def validate_items_type(val):
        for item in val:
            if not isinstance(item, type_):
                raise TypeError('value must be instance of any of {}'
                                .format(str(type_)))
        return True
    return validate_items_type
