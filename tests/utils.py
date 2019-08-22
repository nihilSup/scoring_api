import functools


def cases(cases):
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args):
            try:
                for case in cases:
                    case = case if isinstance(case, tuple) else (case, )
                    f(*args, *case)
            except Exception as e:
                raise type(e)(f'Failed case: {case}') from e
        return inner_wrapper
    return wrapper
