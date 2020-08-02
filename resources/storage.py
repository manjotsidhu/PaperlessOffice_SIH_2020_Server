from flask import request, Response, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine import Q
from database.models import Storage
from resources.utils import allowed_file, UPLOAD_FOLDER, get_user_email, get_user_name, get_user_id, get_user_role
from services.export2excel.export2excel import export_to_excel
from services.smtp.smtp import send_email_async


class StorageApi(Resource):
    @jwt_required
    def post(self):

        if 'file' not in request.files:
            return {'No File Sent'}, 404
        file = request.files['file']
        if file.filename == '':
            return {'No File Selected'}, 404
        if file:
            body = request.form.to_dict()

            file_ext = None
            scan = None
            if 'fileExt' in body:
                file_ext = body['fileExt']
                del body['fileExt']
            if 'scan' in body:
                scan = True
                del body['scan']

            form = Storage(**body)
            form.save(file=file, fileExt=file_ext, scan=scan)
            send_email_async(get_user_email(), 'notification', get_user_name(),
                             notif=f"Your document {form.fileName} has been successfully uploaded and ready to "
                                   f"be used.Please check E-Daftar portal for further updates.")
            return {'id': str(form.id)}, 200
        else:
            return {'Error: Invalid Document'}, 405

    @jwt_required
    def get(self):
        q = Storage.objects(Q(creator=get_jwt_identity()['_id']['$oid']) | Q(visibility='public') | Q(visibility=get_user_role())).order_by('-timestamp')

        if 'limit' in request.args:
            limit = int(request.args['limit'])
            return Response(q[:limit].to_json(), mimetype="application/json", status=200)
        elif 'excel' in request.args:
            return send_from_directory(directory=UPLOAD_FOLDER, filename=export_to_excel(q, get_user_id()))

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

        s = Storage.objects(Q(id=doc_id) & Q(creator=get_jwt_identity()['_id']['$oid'])).get()
        file_name = s.fileName
        s.delete()
        send_email_async(get_user_email(), 'notification', get_user_name(),
                         notif=f"Your document {file_name} has been deleted successfully.")
        return 'Success', 200
