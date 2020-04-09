from functools import wraps

from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_jwt_extended.view_decorators import _decode_jwt_from_request, jwt_required

from database.models import User
from flask_restful import Resource
import datetime


def admin_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        jwt_data, jwt_header = _decode_jwt_from_request(request_type='access')

        if jwt_data['identity']['role'] == 'admin':
            authorized = True
        else:
            authorized = False

        if not authorized:
            raise NoAuthorizationError("You are not admin")

        return view_function(*args, **kwargs)

    return jwt_required(wrapper)


def authority_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        jwt_data, jwt_header = _decode_jwt_from_request(request_type='access')

        if jwt_data['identity']['role'] == 'authority':
            authorized = True
        else:
            authorized = False

        if not authorized:
            raise NoAuthorizationError("You are not admin")

        return view_function(*args, **kwargs)

    return jwt_required(wrapper)


class SignupApi(Resource):
    def post(self):
        body = request.get_json()
        user = User(**body)
        user.save()
        user.add_ca()
        return {'id': str(user.id)}, 200


class LoginApi(Resource):
    def post(self):
        body = request.get_json()
        user = User.objects.get(email=body.get('email'))
        authorized = user.check_password(body.get('password'))
        if not authorized:
            return {'error': 'Email or password invalid'}, 401

        expires = datetime.timedelta(hours=6)
        access_token = create_access_token(identity=user, expires_delta=expires)

        return {'token': access_token}, 200