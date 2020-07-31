import json

from flask import Response, request, send_from_directory
from database.models import User
from mongoengine import Q
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from resources.auth import admin_required
from resources.utils import UPLOAD_FOLDER, get_user_id, get_user_email, get_user_name
from services.export2excel.export2excel import export_to_excel
from services.smtp.smtp import send_email_async


class UsersApi(Resource):
    @jwt_required
    def get(self):
        u = User.objects(Q(role=get_jwt_identity()['role'])).\
                exclude('private_key', 'public_key', 'password')

        if 'unapproved' in request.args:
            u = User.objects(Q(role=get_jwt_identity()['role']) & Q(approved=False)).\
                exclude('private_key', 'public_key', 'password')

        if 'excel' in request.args:
            return send_from_directory(directory=UPLOAD_FOLDER, filename=export_to_excel(u, get_user_id()))

        return Response(u.to_json(), mimetype="application/json", status=200)

    @admin_required
    def post(self):
        body = request.get_json()
        user = User(**body).save()
        return {'id': str(user.id)}, 200


class UserApi(Resource):
    @jwt_required
    def get(self):
        user = User.objects().get(id=get_user_id())
        return Response(user.to_json(), mimetype="application/json", status=200)

    @jwt_required
    def delete(self):
        User.objects.get(id=get_jwt_identity()).delete()
        return '', 200
