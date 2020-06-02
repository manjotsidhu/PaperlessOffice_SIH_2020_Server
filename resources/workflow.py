from flask import request, Response
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from database.models import Workflow
from resources.auth import authority_required


class WorkflowApi(Resource):
    @jwt_required
    @authority_required
    def post(self):
        body = request.get_json()
        workflow = Workflow(**body).save()
        return {'id': str(workflow.id)}, 200

    # @jwt_required
    # def get(self):
    #    workflows = Workflow.objects().to_json()
    #    return Response(workflows, mimetype="application/json", status=200)


class WorkFlowByIdApi(Resource):
    @jwt_required
    def get(self, id):
        return Response(Workflow.objects.get(id=id).to_json(), mimetype="application/json", status=200)

    # TODO: Implement DELETE Workflow
