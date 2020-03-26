
from ellipticcurve.privateKey import PrivateKey, toBytes
from ellipticcurve.publicKey import PublicKey
from mongoengine import CASCADE, ReferenceField

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
    user = db.ReferenceField(User, required=True, unique=True, reverse_delete_rule=CASCADE)
    public_key = db.StringField(required=True)


class Field(db.Document):
    name = db.StringField(required=True)
    type = db.StringField(required=True)
    isRequired = db.BooleanField(default=False)
    maxLength = db.IntField(default=10)


class Form(db.Document):
    creator = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    title = db.StringField(required=True)
    description = db.StringField()
    fields = db.ListField(ReferenceField(Field))

