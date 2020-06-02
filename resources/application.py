from flask import request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine import Q

from database.models import Application, ApplicationTemplate, Workflow, User
from resources.auth import authority_required


class ApplicationsTemplateApi(Resource):

    @jwt_required
    @authority_required
    def post(self):
        body = request.get_json()
        application_template = ApplicationTemplate(**body).save()
        return {'id': str(application_template.id)}, 200

    @jwt_required
    def get(self):
        application_templates = ApplicationTemplate.objects().to_json()
        return Response(application_templates, mimetype="application/json", status=200)


class ApplicationTemplateApi(Resource):

    @jwt_required
    def get(self, id):
        return Response(ApplicationTemplate.objects.get(id=id).to_json(), mimetype="application/json", status=200)

    # TODO: Bringup DELETE Application Template API


class ApplicationsApi(Resource):

    @jwt_required
    def post(self):
        body = request.get_json()
        application = Application(**body).save()
        return {'id': str(application.id)}, 200

    @jwt_required
    def get(self):
        if get_jwt_identity()['role'] == 'authority':
            q = Application.objects(Q(assignedId=get_jwt_identity()['_id']['$oid']) |
                                    Q(creatorId=get_jwt_identity()['_id']['$oid']))
            return Response(q.to_json(), mimetype="application/json", status=200)
        else:
            q = Application.objects(Q(creatorId=get_jwt_identity()['_id']['$oid']))
            return Response(q.to_json(), mimetype="application/json", status=200)


class ApplicationApi(Resource):

    @jwt_required
    def get(self, id):
        return Response(Application.objects(Q(id=id) & (Q(creatorId=get_jwt_identity()['_id']['$oid']) |
                                                        Q(assignedId=get_jwt_identity()['_id']['$oid']))).get().to_json(),
                        mimetype="application/json", status=200)

    @jwt_required
    def delete(self, id):
        print('TODO: Delete Application')


class SigningApi(Resource):

    @jwt_required
    @authority_required
    def post(self, id, action):
        print('TODO: SIGNING Process')
