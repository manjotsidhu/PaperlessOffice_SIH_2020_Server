import os

from flask import Flask
from database.db import initialize_db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

from resources import utils
from resources.routes import initialize_routes

# Create uploads dir
os.makedirs('uploads', exist_ok=True)

# Get .env file, used to store jwt secret key
os.environ["ENV_FILE_LOCATION"] = ".env"

# Initialize Flask
app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
app.config['UPLOAD_FOLDER'] = utils.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
api = Api(app)

# JWT Manager
api.representations = {'application/json': utils.output_json}
jwt = JWTManager(app)


# JWT Blacklist Loader
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in utils.blacklist


# Check if MongoDb Host Url present in environment
# Heroku Web App has this set in environment
# Otherwise use the local database
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    print("USING LOCAL MONGO DB")
    app.config['MONGODB_SETTINGS'] = {
        # Change this for mongodb host
        'host': 'mongodb://localhost:27017/daftar'
    }
else:
    app.config['MONGODB_SETTINGS'] = {
        'host': MONGO_URL
    }

initialize_db(app)
initialize_routes(api)
bCrypt = Bcrypt(app)

if __name__ == '__main__':
    app.run()
