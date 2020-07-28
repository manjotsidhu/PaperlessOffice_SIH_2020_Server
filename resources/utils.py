from flask import make_response
from bson.json_util import dumps
from flask_jwt_extended import get_jwt_identity

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
UPLOAD_FOLDER = 'uploads'

blacklist = set()


def get_user_id():
    return get_jwt_identity()['_id']['$oid']


def get_user_email():
    return get_jwt_identity()['email']


def get_user_name():
    return get_jwt_identity()['first_name']


def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

