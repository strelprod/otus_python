#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from scoring import get_interests, get_score
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


def field_check(check, data):
    if (check is True and data) \
        or check is False:
        return True
    return False


class CharField:
    def __init__(self, 
                 required, 
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
    
    def is_valid(self, data):
        return isinstance(data, str) and \
            field_check(self.nullable, data) and \
            field_check(self.required, data)


class ArgumentsField:
    def __init__(self, 
                 required, 
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable

    def is_valid(self, data):
        return isinstance(data, dict) and \
            field_check(self.nullable, data) and \
            field_check(self.required, data)


class EmailField(CharField):
    pattern = "@"

    def __init__(self, 
                 required, 
                 nullable,
                 *args,
                 **kwargs):
        super().__init__(required, nullable)

    def is_valid(self, data):
        return super().is_valid(data) \
            and self.pattern in data


class PhoneField:
    def __init__(self, 
                 required, 
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable

    def is_valid(self, data):
        return (isinstance(data, str) or isinstance(data, int)) and \
            len(str(data)) == 11 and \
            str(data)[0] == '7' and \
            field_check(self.nullable, data) and \
            field_check(self.required, data)


class DateField:
    dt_format = "%d.%m.%Y"

    def __init__(self, 
                 required, 
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable

    def is_valid(self, data):
        try:
            if data:
                _ = datetime.datetime.strptime(data, self.dt_format)
        except:
            return False
        return field_check(self.nullable, data) and \
            field_check(self.required, data)


class BirthDayField:
    dt_format = "%d.%m.%Y"

    def __init__(self, 
                 required, 
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable

    def is_valid(self, data):
        try:
            if data:
                dt_birth = datetime.datetime.strptime(data, self.dt_format)
                dt_now = datetime.datetime.now()
                year_diff = relativedelta(dt_now, dt_birth).years
                if year_diff > 70:
                    return False
        except:
            return False
        return field_check(self.nullable, data) and \
            field_check(self.required, data)


class GenderField:
    def __init__(self, 
                 required, 
                 nullable,
                 *args,
                 **kwargs):
        self.required = required
        self.nullable = nullable
    
    def is_valid(self, data):
        return field_check(self.nullable, data) and \
            field_check(self.required, data) and \
            isinstance(data, int) and \
            data in GENDERS


class ClientIDsField:
    def __init__(self, 
                 required,
                 *args,
                 **kwargs):
        self.required = required

    def is_valid(self, data):
        if not field_check(self.required, data):
            return False
        for val in data:
            if not isinstance(val, int):
                return False
        return True


class ClientsInterestsRequest:
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)
    
    def __init__(self, params):
        self.params = params

    def execute_method(self, ctx, store, *args, **kwargs):
        invalid = self.validate_params()
        if invalid:
            errors = ", ".join(invalid)
            errors_msg = {
                "error": f"Запрос интересов. Неладины поля: {errors}"
            }
            return errors_msg, INVALID_REQUEST
        client_ids = self.params.get('client_ids')
        ctx['nclients'] = len(client_ids)
        return self.interests_per_cid(client_ids, store), OK

    def interests_per_cid(self, client_ids, store):
        clients = {
            cid: get_interests(store, cid) for cid in client_ids
        }
        return clients
    
    def validate_params(self):
        invalid = []
        if not self.client_ids.is_valid(self.params.get('client_ids')):
            invalid.append('client_ids')
        if not self.date.is_valid(self.params.get('date')):
            invalid.append('client_ids')
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

    data = {
        'first_name': None,
        'last_name': None,
        'email': None,
        'phone': None,
        'birthday': None,
        'gender': None
    }

    default_admin_score = 42
    
    def __init__(self, params):
        self.params = params
        self.valid_pair = None

    def execute_method(self, ctx, store, is_admin, **kwargs):
        if not self.validate_params():
            return {}, INVALID_REQUEST
        ctx['has'] = self.valid_pair
        for field in self.valid_pair:
            self.data[field] = self.params.get(field)
        score = {
            "score": self.client_score(store, 
                                       is_admin,
                                       self.data)
        }
        return score, OK

    def client_score(self, store, is_admin, data):
        if is_admin:
            return self.default_admin_score
        return get_score(store, **self.data)

    def validate_params(self):
        self.valid_pair = []
        for field in self.params:
            val = self.params.get(field)
            if hasattr(self, field):
                if getattr(self, field).is_valid(val):
                    self.valid_pair.append(field)
                else:
                    return False
        for pair in self.valid_pairs:
            if set(self.valid_pair).issubset(set(pair)):
                return True
        

class MethodRequest:
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)
    method_strategies = {
        'clients_interests': ClientsInterestsRequest,
        'online_score': OnlineScoreRequest
    }

    def __init__(self, request, *args, **kwargs):
        self.params = request['body']

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def execute_method(self, ctx, store):
        invalid = self.validate_params()
        if invalid:
            errors = ", ".join(invalid)
            errors_msg = {
                "error": f"Основной запрос. Неладины поля: {errors}"
            }
            return errors_msg, INVALID_REQUEST
        #TODO check_auth()
        method_strategy = self.method_strategies.get(
            self.params.get('method')
        )
        if not method_strategy:
            return {}, NOT_FOUND
        method = method_strategy(self.params['arguments'], self.is_admin)
        return method.execute_method(ctx, store)

    def validate_params(self):
        invalid = []
        if not self.account.is_valid(self.params.get('account')):
            invalid.append('account')
        if not self.login.is_valid(self.params.get('login')):
            invalid.append('account')
        if not self.token.is_valid(self.params.get('token')):
            invalid.append('account')
        if not self.arguments.is_valid(self.params.get('arguments')):
            invalid.append('account')
        if not self.method.is_valid(self.params.get('method')):
            invalid.append('account')
        return invalid


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    get_result = MethodRequest(request)
    response, code = get_result.execute_method(ctx, store)
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
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
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
        self.wfile.write(json.dumps(r).encode('utf-8'))
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
