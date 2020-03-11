from flask import Response, request
from database.models import User
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from resources.auth import admin_required


class UsersApi(Resource):
    @admin_required
    def get(self):
        u = User.objects().to_json()
        return Response(u, mimetype="application/json", status=200)

    @admin_required
    def post(self):
        body = request.get_json()
        user = User(**body).save()
        id = user.id
        return {'id': str(id)}, 200


class UserApi(Resource):
    @jwt_required
    def get(self):
        user = get_jwt_identity()
        print(user)
        u = User.objects.get(username='user').to_json()
        return Response(u, mimetype="application/json", status=200)

    @jwt_required
    def delete(self):
        u = User.objects.get(id=get_jwt_identity()).delete()
        return '', 200
