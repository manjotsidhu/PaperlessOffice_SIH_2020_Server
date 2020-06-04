import json

from flask import Response, request
from database.models import User, Ca
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
        return {'id': str(user.id)}, 200


class UserApi(Resource):
    @jwt_required
    def get(self):
        user = get_jwt_identity()
        return Response(json.dumps(user), mimetype="application/json", status=200)

    @jwt_required
    def delete(self):
        # TODO: FIX THIS
        User.objects.get(id=get_jwt_identity()).delete()
        Ca.objects.get(user_id=get_jwt_identity()).delete()
        return '', 200
