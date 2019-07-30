import json
import datetime
import logging
import hashlib
import uuid
import abc
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from dateutil.relativedelta import relativedelta

from scoring_api import field
from scoring_api import scoring

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


def has_length(length):
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
    def valdiate_date(val):
        datetime.datetime.strptime(val, fmt)
        return True
    return valdiate_date


def is_age_le(years, fmt):
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
        if not isinstance(val, tuple(type_)):
            raise TypeError('value must be instance of any of {}'
                            .format(str(type_)))
        else:
            return True
    return validate_type


class CharField(field.BaseField, field.TypedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, type_=[str])


class ArgumentsField(field.BaseField, field.TypedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, type_=[dict])


class CommonField(field.BaseField, field.TypedField):
    """alias for BaseField and TypedField"""
    pass


class EmailField(CommonField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, validators=[check_if_email], type_=[str])


class PhoneField(CommonField):
    def __init__(self, length, prefix, **kwargs):
        super().__init__(**kwargs, type_=[str, int],
                         validators=[has_length(length),
                                     starts_with(prefix)])


class DateField(CommonField):
    def __init__(self, fmt, **kwargs):
        super().__init__(**kwargs, type_=[str],
                         validators=[is_date(fmt)])


class BirthDayField(CommonField):
    def __init__(self, fmt, years, **kwargs):
        super().__init__(**kwargs, type_=[str],
                         validators=[is_date(fmt), is_age_le(years, fmt)])


class GenderField(CommonField):
    def __init__(self, range_, **kwargs):
        super().__init__(**kwargs, type_=[int],
                         validators=[int_in_range(range_)])


class ClientIDsField(CommonField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, type_=[list])


class Request(abc.ABC):
    def __init__(self, request):
        self.valid = True
        for attr_name, attr_value in request.items():
            setattr(self, attr_name, attr_value)

    def fields(self):
        for attr_name, attr_val in self.__class__.__dict__.items():
            if isinstance(attr_val, field.ValidatedField):
                yield attr_name, attr_val

    @abc.abstractmethod
    def validate(self):
        invalid_fields = []
        for attr_name, attr_val in self.fields():
            msg, valid = attr_val.validate(self)
            if not valid:
                invalid_fields.append(attr_name)
        if invalid_fields:
            msg = "invalid fields: " + ', '.join(invalid_fields)
            return msg, INVALID_REQUEST
        else:
            return "", OK

    def as_dict(self):
        return dict((name, val) for name, val in self.fields())


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True, fmt='%d.%m.%Y')


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True, length=11, prefix='7')
    birthday = BirthDayField(required=False, nullable=True,
                             fmt='%d.%m.%Y', years=70)
    gender = GenderField(range_=[0, 1, 2], required=False, nullable=True)

    def validate(self):
        status, msg = super().validate()
        if status != OK:
            return msg, status
        if (self.phone and self.email or self.first_name and self.last_name or
           birthday and not (gender is None)):
            return "", OK
        else:
            return "There is no available field pairs", INVALID_REQUEST

    @property
    def has(self):
        return [field_name for field_name, field in self.fields()
                if getattr(self, field_name) is not None]


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

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
    method_request = MethodRequest(request)
    if not check_auth(method_request):
        return ERRORS[FORBIDDEN], FORBIDDEN
    msg, code = method_request.validate()
    if code != OK:
        return msg, code
    if method_request.method == 'online_score':
        conc_method_req = OnlineScoreRequest(method_request.arguments)
        msg, code = conc_method_req.validate()
        if code != OK:
            return msg, code
        ctx['has'] = conc_method_req.has
        if method_request.is_admin:
            return {'score': 42}, OK
        else:
            return {'score': scoring.get_score(**conc_method_req.as_dict)}, OK
    elif method_request.method == 'clients_interests':
        conc_method_req = ClientsInterestsRequest(method_request.arguments)
        msg, code = conc_method_req.validate()
        if code != OK:
            return msg, code
        
    else:
        return ERRORS[NOT_FOUND], "Unknown method - %s" % method_request.method
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
