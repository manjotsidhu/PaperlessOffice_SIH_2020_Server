import os

from bson.json_util import dumps
from flask import Flask, make_response
from database.db import initialize_db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

from resources.routes import initialize_routes
from resources.utils import UPLOAD_FOLDER

os.environ["ENV_FILE_LOCATION"] = ".env"

app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs('uploads', exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

api = Api(app)


def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


api.representations = {'application/json': output_json}
jwt = JWTManager(app)

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    print("USING LOCAL MONGO DB")
    app.config['MONGODB_SETTINGS'] = {
        'host': 'mongodb://localhost:27017/daftar'
    }
else:
    app.config['MONGODB_SETTINGS'] = {
        'host': MONGO_URL
    }

initialize_db(app)
initialize_routes(api)
bcrypt = Bcrypt(app)

if __name__ == '__main__':
    app.run()
