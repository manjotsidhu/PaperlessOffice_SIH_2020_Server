import json

from flask import Response
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource


class IndexApi(Resource):
    def get(self):
        user = get_jwt_identity()
        if user is not None:
            print(type(user))
            return Response(json.dumps(user), mimetype="application/json", status=200)
        else:
            return Response("Paperless Office REST API Server functional.", mimetype="application/json", status=200)
