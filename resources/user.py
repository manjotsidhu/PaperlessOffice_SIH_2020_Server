from flask import Response, request
from database.models import User
from flask_restful import Resource
from flask_jwt_extended import jwt_required

class UsersApi(Resource):
    @jwt_required
    def get(self):
        u = User.objects().to_json()
        return Response(u, mimetype="application/json", status=200)

    @jwt_required
    def post(self):
        body = request.get_json()
        user = User(**body).save()
        id = user.id
        return {'id': str(id)}, 200


class UserApi(Resource):
    @jwt_required
    def get(self, id):
        u = User.objects.get(id=id).to_json()
        return Response(u, mimetype="application/json", status=200)

    @jwt_required
    def delete(self, id):
        u = User.objects.get(id=id).delete()
        return '', 200
