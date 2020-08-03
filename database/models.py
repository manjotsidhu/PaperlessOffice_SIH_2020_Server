import datetime
import hashlib
import json
import os
import time

from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.publicKey import PublicKey
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import get_jwt_identity
from mongoengine import ReferenceField

from resources.utils import get_file_extension, UPLOAD_FOLDER, random_pin
from services.scanner.scanning import scanner
from .db import db


class User(db.Document):
    email = db.StringField(required=True, unique=True)
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    password = db.StringField(required=True, min_length=6)
    dob = db.StringField(required=True)
    role = db.StringField(default='user')
    costOfPaper = db.DecimalField(default=0.50)
    verified = db.BooleanField(default=False)
    verification_pin = db.StringField(default=str(random_pin(6)))
    approved = db.BooleanField(default=False)
    private_key = db.StringField()
    public_key = db.StringField()

    def save(self, *args, **kwargs):
        if self.role == 'user':
            self.approved = True

        self.generate_keys()
        self.hash_password()

        super(User, self).save(*args, **kwargs)

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
        ca = Ca(user=str(self.id), public_key=self.public_key)
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

    def __init__(self, *args, **kwargs):
        db.Document.__init__(self, *args, **kwargs)

        self.creator = get_jwt_identity()['_id']['$oid']


class Storage(db.Document):
    # TODO: sharedTo Field
    creator = db.StringField(required=True)
    file = db.StringField()
    fileExtension = db.StringField()
    fileName = db.StringField(required=True)
    fileDescription = db.StringField()
    visibility = db.StringField(default='private')
    timestamp = db.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def __init__(self, *args, **kwargs):
        db.Document.__init__(self, *args, **kwargs)

        self.creator = get_jwt_identity()['_id']['$oid']

    def save(self, *args, **kwargs):
        self.save_file(kwargs['file'], kwargs['fileExt'], kwargs['scan'])

        super(Storage, self).save(*args, **kwargs)

    def save_file(self, file, file_ext, scan):
        if file_ext is None:
            self.fileExtension = get_file_extension(file.filename)
        else:
            self.fileExtension = file_ext
        self.file = get_jwt_identity()['_id']['$oid'] + "_" + time.strftime("%Y%m%d-%H%M%S") + "." + self.fileExtension

        if scan:
            fileName = get_jwt_identity()['_id']['$oid'] + "_" + time.strftime(
                "%Y%m%d-%H%M%S")

            input = os.path.join(UPLOAD_FOLDER, self.file)
            output = os.path.join(UPLOAD_FOLDER, fileName + "_scanned." + self.fileExtension)
            file.save(input)

            scanner(input, output)
            self.file = fileName + "_scanned." + self.fileExtension
        else:
            file.save(os.path.join(UPLOAD_FOLDER, self.file))


class Stage(db.Document):
    authId = db.StringField(required=True)
    authName = db.StringField(required=True)
    name = db.StringField(required=True)


class Workflow(db.Document):
    name = db.StringField(required=True)
    creatorId = db.StringField(required=True)
    creatorName = db.StringField(required=True)
    timestamp = db.DateTimeField(required=True, default=datetime.datetime.utcnow)
    totalStages = db.IntField(required=True)
    stages = db.ListField()

    def __init__(self, *args, **kwargs):
        db.Document.__init__(self, *args, **kwargs)

        for stage in self.stages:
            if 'authId' not in stage:
                data = User.objects.aggregate([
                    {"$match": {"role": stage['role']}},
                    {"$sample": {"size": 1}}
                ])

                for d in data:
                    stage['authId'] = str(d['_id'])
                    stage['authName'] = str(d['first_name']) + " " + str(d['last_name'])

        if self.creatorId is None:
            self.creatorId = get_jwt_identity()['_id']['$oid']

        if self.creatorName is None:
            user = User.objects.get(id=self.creatorId)
            self.creatorName = user.first_name + " " + user.last_name


class ApplicationTemplate(db.Document):
    name = db.StringField(required=True)
    creatorId = db.StringField(required=True)
    creatorName = db.StringField(required=True)
    workflowId = db.StringField(required=True)
    formId = db.StringField(required=True)
    stages = db.IntField(required=True)
    timestamp = db.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def __init__(self, *args, **kwargs):
        db.Document.__init__(self, *args, **kwargs)

        self.stages = Workflow.objects.get(id=self.workflowId).totalStages

        if self.creatorId is None:
            self.creatorId = get_jwt_identity()['_id']['$oid']

        if self.creatorName is None:
            user = User.objects.get(id=self.creatorId)
            self.creatorName = user.first_name + " " + user.last_name


class Application(db.Document):
    name = db.StringField(required=True)
    description = db.StringField(required=True)
    message = db.StringField(required=True)
    creatorId = db.StringField(required=True)
    templateId = db.StringField(required=True)
    creatorName = db.StringField(required=True)
    workflowId = db.StringField(required=True)
    assignedId = db.StringField(required=True)
    assignedName = db.StringField(required=True)
    formId = db.StringField(required=True)
    form = db.DictField(required=True)
    status = db.IntField(required=True, default=0)
    stage = db.IntField(required=True, default=0)
    stages = db.IntField(required=True)
    timestamp = db.DateTimeField(required=True, default=datetime.datetime.utcnow)
    hash = db.StringField(required=True)
    signatures = db.ListField(db.StringField())

    def __init__(self, *args, **kwargs):
        db.Document.__init__(self, *args, **kwargs)

        template = ApplicationTemplate.objects.get(id=self.templateId)
        workflow = Workflow.objects.get(id=template.workflowId)

        if self.description is None:
            self.description = ''

        if self.message is None:
            self.message = ''

        if self.workflowId is None or self.formId is None:
            self.workflowId = template.workflowId
            self.formId = template.formId

        if self.stages is None:
            self.stages = Workflow.objects.get(id=self.workflowId).totalStages

        if self.name is None:
            self.name = template.name

        if self.creatorId is None:
            self.creatorId = get_jwt_identity()['_id']['$oid']

        if self.assignedId is None:
            self.assignedId = workflow.stages[self.stage]['authId']
            self.assignedName = workflow.stages[self.stage]['authName']

        if self.creatorName is None:
            user = User.objects.get(id=self.creatorId)
            self.creatorName = user.first_name + " " + user.last_name

        if not self.hash:
            self.hash = self.to_hash()

        if not self.signatures:
            signatures = [''] * self.stages
            for i in range(self.stages):
                signatures[i] = ''

            self.signatures = signatures

    # Calculate Hash based on creatorId, templateId, workflowId, formId, form
    def to_hash(self):
        return hashlib.md5(json.dumps({
            "creatorId": self.creatorId,
            "templateId": self.templateId,
            "workflowId": self.workflowId,
            "formId": self.formId,
            "form": self.form
        }, sort_keys=True).encode("utf-8")).hexdigest()
