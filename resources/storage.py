from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from database.models import File
from resources.utils import allowed_file


class StorageApi(Resource):
    @jwt_required
    def post(self):

        if 'file' not in request.files:
            return {'No File Sent'}, 404
        file = request.files['file']
        if file.filename == '':
            return {'No File Selected'}, 403
        if file and allowed_file(file.filename):
            body = request.form.to_dict()
            form = File(**body)
            form.save_file(file)
            form.save()
            return {'File Uploaded'}, 200
        else:
            return {'Error: Invalid Document'}, 405

    @jwt_required
    def get(self):
        #TODO
        return

    @jwt_required
    def delete(self):
        #TODO
        return

    @jwt_required
    def update(self):
        return
