from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Document):
    email = db.StringField(required=True, unique=True)
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    password = db.StringField(required=True, min_length=6)
    dob = db.DateTimeField()
    role = db.StringField(default='user')

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class CA(db.Document):
    user_id = db.StringField(required=True, unique=True)
    public_key = db.StringField(required=True)
