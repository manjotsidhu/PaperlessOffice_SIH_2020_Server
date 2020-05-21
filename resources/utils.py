from flask import make_response
from bson.json_util import dumps

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])
UPLOAD_FOLDER = 'uploads'

blacklist = set()


def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

