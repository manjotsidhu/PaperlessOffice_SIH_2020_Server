import bson
from flask_jwt_extended import jwt_required

from flask_restful import Resource
from flask import Response, request, jsonify

from database.models import Form, Field


class SaveFormApi(Resource):
    @jwt_required
    def post(self):
        body = request.get_json()
        form = Form(**body).save()
        print(Field.objects)
        return {'id': str(form.id)}, 200


class GetFormApi(Resource):
    @jwt_required
    def get(self, id):
        return Response(Form.objects.get(id=id).to_json(), mimetype="application/json", status=200)
