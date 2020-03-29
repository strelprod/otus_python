#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from weakref import WeakKeyDictionary
from dateutil.relativedelta import relativedelta
from scoring import get_interests, get_score


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
DEFAULT_FIELD_VAL = "REQUIRED_FIELD_IS_NONE"


class CharField:
    def __init__(self,
                 required,
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        if (self.required is True and value == DEFAULT_FIELD_VAL) or \
            (not isinstance(value, str)) or \
            (self.nullable is False and (value == "" or value is None)):
            raise ValueError(f"Incorrect CharField value: {value}")
        elif value == DEFAULT_FIELD_VAL:
            self.data[instance] = None
        else:
            self.data[instance] = value


class ArgumentsField:
    def __init__(self,
                 required,
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        if (self.required is True and value == DEFAULT_FIELD_VAL) or \
            (not isinstance(value, dict)) or \
            (self.nullable is False and (value == {} or value is None)):
            raise ValueError(f"Incorrect ArgumentsField value: {value}")
        elif value == DEFAULT_FIELD_VAL:
            self.data[instance] = None
        else:
            self.data[instance] = value


class EmailField(CharField):
    pattern = "@"

    def __init__(self,
                 required,
                 nullable,
                 *args,
                 **kwargs):
        super().__init__(required, nullable)

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        super().__set__(instance, value)
        if self.pattern not in value:
            self.data.pop(instance, None)
            raise ValueError(f"Incorrect EmailField value: {value}")


class PhoneField:
    def __init__(self,
                 required,
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        if (self.required is True and value == DEFAULT_FIELD_VAL) or \
            (not (isinstance(value, str) or isinstance(value, int))) or \
            (self.nullable is False and (value == "" or value == 0 or value is None)) or \
            (not (len(str(value)) == 11 and str(value)[0] == '7')):
            raise ValueError(f"Incorrect PhoneField value: {value}")
        elif value == DEFAULT_FIELD_VAL:
            self.data[instance] = None
        else:
            self.data[instance] = value


class DateField:
    dt_format = "%d.%m.%Y"

    def __init__(self,
                 required,
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        try:
            if value and value != DEFAULT_FIELD_VAL:
                value = datetime.datetime.strptime(value, self.dt_format)
        except:
            raise ValueError(f"Incorrect DateField value: {value}")
        if (self.required is True and value == DEFAULT_FIELD_VAL) or \
            (self.nullable is False and (value == "" or value is None)):
            raise ValueError(f"Incorrect DateField value: {value}")
        elif value == DEFAULT_FIELD_VAL:
            self.data[instance] = None
        else:
            self.data[instance] = value


class BirthDayField:
    dt_format = "%d.%m.%Y"

    def __init__(self,
                 required,
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, dt_birth):
        try:
            if dt_birth and dt_birth != DEFAULT_FIELD_VAL:
                dt_birth = datetime.datetime.strptime(dt_birth, self.dt_format)
                dt_now = datetime.datetime.now()
                year_diff = relativedelta(dt_now, dt_birth).years
        except:
            raise ValueError(f"Incorrect BirthDayField value: {dt_birth}")
        if (self.required is True and dt_birth == DEFAULT_FIELD_VAL) or \
            (self.nullable is False and (dt_birth == "" or dt_birth is None)) or \
            year_diff > 70:
            raise ValueError(f"Incorrect BirthDayField value: {dt_birth}")
        elif dt_birth == DEFAULT_FIELD_VAL:
            self.data[instance] = None
        else:
            self.data[instance] = dt_birth


class GenderField:
    def __init__(self,
                 required,
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        if (self.required is True and value == DEFAULT_FIELD_VAL) or \
            (not isinstance(value, int)) or \
            (value not in GENDERS):
            raise ValueError(f"Incorrect GenderField value: {value}")
        elif value == DEFAULT_FIELD_VAL:
            self.data[instance] = None
        else:
            self.data[instance] = value


class ClientIDsField:
    def __init__(self,
                 required,
                 *args,
                 **kwargs):
        self.required = required
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)

    def __set__(self, instance, value):
        if (self.required is True and value == DEFAULT_FIELD_VAL) or \
            (not isinstance(value, list) or not value):
            raise ValueError(f"Incorrect ClientIDsField value: {value}")
        for val in value:
            if not isinstance(val, int):
                raise ValueError(f"Incorrect ClientIDsField value: {val}")
        self.data[instance] = value


class ClientsInterestsRequest:
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)
    request_fileds = ['client_ids', 'date']

    def __init__(self, params, ctx, store, *args, **kwargs):
        self.params = params
        self.ctx = ctx
        self.store = store

    def execute_method(self):
        invalid = self.validate_params()
        if invalid:
            errors = ", ".join(invalid)
            errors_msg = {
                "error": f"ClientsInterestsRequest. Invalid fields: {errors}"
            }
            return errors_msg, INVALID_REQUEST
        self.ctx['nclients'] = len(self.client_ids)
        return self.interests_per_cid(self.client_ids, self.store), OK

    def interests_per_cid(self, client_ids, store):
        clients = {
            cid: get_interests(store, cid) for cid in client_ids
        }
        return clients

    def set_param(self, field, value):
        try:
            setattr(self, field, value)
            return True
        except ValueError:
            return False

    def validate_params(self):
        invalid = []
        for param in self.request_fileds:
            if not self.set_param(param, self.params.get(param, DEFAULT_FIELD_VAL)):
                invalid.append(param)
        return invalid


class OnlineScoreRequest:
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    valid_pairs = [
        (
            'first_name', 'last_name', 'email',
            'phone', 'birthday', 'gender'
        ),
        ('phone', 'email'),
        ('first_name', 'last_name'),
        ('gender', 'birthday')
    ]

    default_admin_score = 42

    def __init__(self,
                 params,
                 ctx,
                 store,
                 is_admin,
                 *args,
                 **kwargs):
        self.params = params
        self.ctx = ctx
        self.store = store
        self.is_admin = is_admin
        self.valid_pair = None

    def execute_method(self):
        if not self.validate_params():
            error_msg = {
                "error": f"OnlineScoreRequest. Valid pairs was not found"
            }
            return error_msg, INVALID_REQUEST

        self.ctx['has'] = self.valid_pair

        score = {
            "score": self.client_score(self.is_admin,
                                       self.store)
        }
        return score, OK

    def client_score(self, is_admin, store):
        if is_admin:
            return self.default_admin_score
        return get_score(store,
                         self.phone,
                         self.email,
                         self.birthday,
                         self.gender,
                         self.first_name,
                         self.last_name)

    def set_param(self, field, value):
        try:
            setattr(self, field, value)
            return True
        except ValueError:
            return False

    def validate_params(self):
        self.valid_pair = []
        for field in self.params:
            val = self.params.get(field, DEFAULT_FIELD_VAL)
            if hasattr(self, field):
                if not self.set_param(field, val):
                    return False
                self.valid_pair.append(field)

        if not self.valid_pair:
            return False

        for pair in self.valid_pairs:
            if set(pair).issubset(set(self.valid_pair)):
                return True


class MethodRequest:
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)
    request_fileds = [
        'account', 'login', 'token',
        'arguments', 'method'
    ]
    method_strategies = {
        'clients_interests': ClientsInterestsRequest,
        'online_score': OnlineScoreRequest
    }

    def __init__(self, request, ctx, store, *args, **kwargs):
        self.params = request['body']
        self.request = request
        self.ctx = ctx
        self.store = store
        self.args = args
        self.kwargs = kwargs

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def execute_method(self):
        invalid = self.validate_params()
        if invalid:
            errors = ", ".join(invalid)
            errors_msg = {
                "error": f"MethodRequest. Invalid fields: {errors}"
            }
            return errors_msg, INVALID_REQUEST

        if not check_auth(self):
            return {}, FORBIDDEN

        method_strategy = self.method_strategies.get(
            self.params.get('method')
        )
        if not method_strategy:
            return {}, NOT_FOUND
        method = method_strategy(self.params['arguments'],
                                 self.ctx,
                                 self.store,
                                 self.is_admin,
                                 *self.args,
                                 **self.kwargs)
        return method.execute_method()

    def set_param(self, field, value):
        try:
            setattr(self, field, value)
            return True
        except ValueError:
            return False

    def validate_params(self):
        invalid = []
        for param in self.request_fileds:
            if not self.set_param(param, self.params.get(param, DEFAULT_FIELD_VAL)):
                invalid.append(param)
        return invalid


def check_auth(request):
    if request.is_admin:
        dt = datetime.datetime.now().strftime("%Y%m%d%H")
        token_data = (dt + ADMIN_SALT).encode('utf-8')
        digest = hashlib.sha512(token_data).hexdigest()
    else:
        token_data = (request.account + request.login + SALT).encode('utf-8')
        digest = hashlib.sha512(token_data).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    get_result = MethodRequest(request, ctx, store)
    response, code = get_result.execute_method()
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
                        {
                            "body": request,
                            "headers": self.headers
                        },
                        context,
                        self.store
                    )
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
            r = {"error": response.get("error") or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('utf-8'))


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', 
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
