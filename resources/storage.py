from flask import request, Response, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine import Q
from database.models import Storage
from resources.utils import allowed_file, UPLOAD_FOLDER


class StorageApi(Resource):
    @jwt_required
    def post(self):

        if 'file' not in request.files:
            return {'No File Sent'}, 404
        file = request.files['file']
        if file.filename == '':
            return {'No File Selected'}, 404
        if file and allowed_file(file.filename):
            body = request.form.to_dict()
            form = Storage(**body)
            form.save(file=file)
            return {'id': str(form.id)}, 200
        else:
            return {'Error: Invalid Document'}, 405

    @jwt_required
    def get(self):
        q = Storage.objects(Q(creator=get_jwt_identity()['_id']['$oid']) | Q(visibility='public'))

        if 'limit' in request.args:
            limit = int(request.args['limit'])
            return Response(q[:limit].to_json(), mimetype="application/json", status=200)

        return Response(q.to_json(), mimetype="application/json", status=200)


class UserStorageApi(Resource):

    @jwt_required
    def get(self, doc_id):
        if 'download' in request.args:
            q = Storage.objects(Q(id=doc_id) & (Q(creator=get_jwt_identity()['_id']['$oid']) | Q(visibility='public')))
            return send_from_directory(directory=UPLOAD_FOLDER, filename=q[0].file)

        return Response(Storage.objects(Q(id=doc_id) & (Q(creator=get_jwt_identity()['_id']['$oid']) |
                                                        Q(visibility='public'))).get().to_json(),
                        mimetype="application/json", status=200)

    @jwt_required
    def update(self, doc_id):
        # TODO
        return

    @jwt_required
    def delete(self, doc_id):
        Storage.objects(Q(id=doc_id) & Q(creator=get_jwt_identity()['_id']['$oid'])).get().delete()
        return '', 200
