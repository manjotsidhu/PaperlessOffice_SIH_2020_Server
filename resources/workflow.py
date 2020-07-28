from flask import request, Response, send_from_directory
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from database.models import Workflow
from resources.auth import authority_required
from resources.utils import get_user_email, get_user_name, UPLOAD_FOLDER, get_user_id
from services.export2excel.export2excel import export_to_excel
from services.smtp.smtp import send_email_async


class WorkflowApi(Resource):
    @jwt_required
    @authority_required
    def post(self):
        body = request.get_json()
        workflow = Workflow(**body).save()
        send_email_async(get_user_email(), 'notification', get_user_name(),
                         notif=f"Workflow {workflow.name} has been successfully created and ready to be used. Please "
                               f"check E-Daftar portal for more updates.")
        return {'id': str(workflow.id)}, 200

    @jwt_required
    def get(self):
        workflows = Workflow.objects()

        if 'excel' in request.args:
            return send_from_directory(directory=UPLOAD_FOLDER, filename=export_to_excel(workflows, get_user_id()))

        return Response(workflows.to_json(), mimetype="application/json", status=200)


class WorkFlowByIdApi(Resource):
    @jwt_required
    def get(self, id):
        return Response(Workflow.objects.get(id=id).to_json(), mimetype="application/json", status=200)

    # TODO: Implement DELETE Workflow
