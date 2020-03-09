import os

from flask import Flask
from database.db import initialize_db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api
from resources.routes import initialize_routes

app = Flask(__name__)
os.environ["ENV_FILE_LOCATION"] = ".env"
app.config.from_envvar('ENV_FILE_LOCATION')
api = Api(app)
jwt = JWTManager(app)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017/daftar'
}

initialize_db(app)
initialize_routes(api)
bcrypt = Bcrypt(app)

app.run()