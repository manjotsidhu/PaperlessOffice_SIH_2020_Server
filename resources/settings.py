import json

from flask import Response
from database.models import User
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from resources.utils import get_user_id


class UserSettingsApi(Resource):
    @jwt_required
    def get(self, key):
        user = User.objects.get(id=get_user_id())

        return {"result": getattr(user, key)}, 200


class UserSettingsPostApi(Resource):
    @jwt_required
    def post(self, key, value):
        user = User.objects.get(id=get_user_id())

        if key == "costOfPaper":
            user.update(costOfPaper=value)
            return Response({"Success": "200"}, mimetype="application/json", status=200)
        else:
            return "Not Permitted", 401
