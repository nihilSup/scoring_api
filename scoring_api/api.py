import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from dateutil.relativedelta import relativedelta

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class TypedField(object):
    __count = 0

    def __init__(self, type_, default=None, name=None):
        self.type = type_
        self.default = default
        cls = self.__class__
        if not name:
            name = '_{}_{}_#{}'.format(self.cls.__name__, type_.__name__,
                                       cls.__count)
        self.name = name
        cls.__count += 1

    def __get__(self, obj, owner):
        if not obj:
            return self
        return getattr(obj, self.name, self.default)

    def __set__(self, obj, val):
        if any(map(lambda t: isinstance(val, t), self.type)):
            setattr(obj, self.name, val)
        else:
            raise TypeError('value must be instance of any of {}'
                            .format(str(self.type)))

    def __set_name__(self, owner, name):
        self.name = name


class NamedDescrMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        for attr_name, attr_val in attrs:
            if isinstance(attr_val, TypedField):
                attr_val.__set_name__(cls, attr_name)


class BaseField(TypedField):
    def __init__(self, required, nullable, validators=None, *args, **kwargs):
        self.required = required
        self.nullable = nullable
        if not validators:
            self.validators = []
        self.val_set_flag = False
        super().__init__(*args, **kwargs)

    def __set__(self, obj, val):
        if not self.nullable and val is None:
            raise ValueError("Value is required, can't be None")
        for validator in self.validators:
            validator(val)
        self.val_set_flag = True
        super().__set__(obj, val)

    def __get__(self, obj, owner):
        if self.required and not self.val_set_flag:
            raise ValueError("Value has been not set, but it is required")
        return super().__get__(obj, owner)


def has_length(length):
    def valdiate_length(val):
        cur_length = len(str(val))
        if cur_length != length:
            raise ValueError('Incorrect length. Expected {}, but got {}'
                             .format(length, cur_length))
    return valdiate_length


def starts_with(char):
    def validate_prefix(val):
        first = str(val)[0]
        if first != char:
            raise ValueError('Incorrect prefix. Expected {}, but got {}'
                             .format(char, first))
    return validate_prefix


def check_if_email(val):
    if '@' not in val:
        raise ValueError('There is no @ in email field')


def is_date(fmt):
    def valdiate_date(val):
        datetime.datetime.strptime(val, fmt)
    return valdiate_date


def is_age_le(years, fmt):
    def validate_age(val):
        bday = datetime.datetime.strptime(val, fmt)
        now = datetime.datetime.now()
        if relativedelta(now, bday).years > years:
            raise ValueError('Age is bigger then {}'.format(years))
    return validate_age


def int_in_range(range_):
    def validate_int_in_range(val):
        if val not in range_:
            raise ValueError('Value: {} not in range'.format(val))
    return validate_int_in_range


class CharField(BaseField):
    def __init__(self, required, nullable):
        super().__init__(required, nullable, type_=[str])


class ArgumentsField(BaseField):
    def __init__(self, required, nullable):
        super().__init__(required, nullable, type_=[dict])


class EmailField(BaseField):
    def __init__(self, required, nullable):
        super().__init__(required, nullable, validators=[check_if_email])


class PhoneField(BaseFiled):
    def __init__(self, required, nullable, length, prefix):
        super().__init__(required, nullable, type_=[str, int],
                         validators=[has_length(length),
                                     starts_with(prefix)])


class DateField(BaseField):
    def __init__(self, required, nullable, fmt):
        super().__init__(required, nullable, type_=[str],
                         validators=[is_date(fmt)])


class BirthDayField(BaseField):
    def __init__(self, required, nullable, fmt, years):
        super().__init__(required, nullable, type_=[str],
                         validators=[is_date(fmt), is_age_le(fmt, years=70)])


class GenderField(BaseField):
    def __init__(self, required, nullable, range_):
        super().__init__(required, nullable, type_=[int],
                         validators=[int_in_range(range_)])


class ClientIDsField(BaseField):
    def __init__(self, required, nullable):
        super().__init__(required, nullable, type_=[list])


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True, fmt='%d.%m.%Y')


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True, length=11, prefix='7')
    birthday = BirthDayField(required=False, nullable=True,
                             fmt='%d.%m.%Y', years=70)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(object):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, account, login, token, arguments, method):
        self.account = account
        self.login = login
        self.token = token
        self.arguments = arguments
        self.method = method

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") +
                                ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = None, None
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request,
                         "headers": self.headers},
                        context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
