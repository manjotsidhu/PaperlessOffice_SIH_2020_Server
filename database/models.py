import datetime
import os
import time

from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.publicKey import PublicKey
from flask_jwt_extended import get_jwt_identity
from mongoengine import CASCADE, ReferenceField

from resources.utils import get_file_extension, UPLOAD_FOLDER
from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Document):
    email = db.StringField(required=True, unique=True)
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    password = db.StringField(required=True, min_length=6)
    dob = db.StringField(required=True)
    role = db.StringField(default='user')
    private_key = db.StringField()
    public_key = db.StringField()

    def generate_keys(self):
        pr_key = PrivateKey()
        self.private_key = str(pr_key.toPem())
        self.public_key = str(pr_key.publicKey().toPem())

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_public_key(self):
        return PublicKey.fromPem(self.public_key)

    def add_ca(self):
        ca = Ca(user=self, public_key=self.public_key)
        ca.save()


class Ca(db.Document):
    user = db.StringField(required=True, unique=True)
    public_key = db.StringField(required=True)


class Field(db.Document):
    name = db.StringField(required=True)
    type = db.StringField(required=True)
    isRequired = db.BooleanField(default=False)
    maxLength = db.IntField(default=10)


class Form(db.Document):
    creator = db.StringField(required=True)
    title = db.StringField(required=True)
    description = db.StringField()
    fields = db.ListField(ReferenceField(Field))


class Storage(db.Document):
    # TODO: sharedTo Field
    creator = db.StringField(required=True)
    file = db.StringField()
    fileExtension = db.StringField()
    fileName = db.StringField(required=True)
    fileDescription = db.StringField()
    visibility = db.StringField(default='private')
    timestamp = db.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def save_file(self, file):
        self.fileExtension = get_file_extension(file.filename)
        self.file = get_jwt_identity()['_id']['$oid'] + "_" + time.strftime("%Y%m%d-%H%M%S") + "." + self.fileExtension

        file.save(os.path.join(UPLOAD_FOLDER, self.file))
