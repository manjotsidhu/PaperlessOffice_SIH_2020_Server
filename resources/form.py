from flask_jwt_extended import jwt_required

from flask_restful import Resource
from flask import Response, request, send_from_directory

from database.models import Form
from resources.utils import UPLOAD_FOLDER, get_user_id
from services.export2excel.export2excel import export_to_excel


class FormApi(Resource):
    @jwt_required
    def post(self):
        body = request.get_json()
        form = Form(**body).save()
        return {'id': str(form.id)}, 200

    @jwt_required
    def get(self):
        forms = Form.objects()

        if 'excel' in request.args:
            return send_from_directory(directory=UPLOAD_FOLDER, filename=export_to_excel(forms, get_user_id()))

        return Response(forms.to_json(), mimetype="application/json", status=200)


class GetFormApi(Resource):
    @jwt_required
    def get(self, id):
        return Response(Form.objects.get(id=id).to_json(), mimetype="application/json", status=200)
