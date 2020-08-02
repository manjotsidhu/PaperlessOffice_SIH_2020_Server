import json

from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey
from flask import request, Response, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine import Q

from database.models import Application, ApplicationTemplate, Workflow, User
from resources.auth import authority_required
from resources.utils import get_user_email, get_user_name, UPLOAD_FOLDER, get_user_id
from services.export2excel.export2excel import export_to_excel
from services.smtp.smtp import send_email_async


class ApplicationsTemplateApi(Resource):

    @jwt_required
    @authority_required
    def post(self):
        body = request.get_json()
        application_template = ApplicationTemplate(**body).save()
        send_email_async(get_user_email(), 'notification', get_user_name(),
                         notif=f"Your Application Template {application_template.name} has been successfully uploaded "
                               f"and ready to be used by the users.Please check E-Daftar portal for more "
                               f"updates.")
        return {'id': str(application_template.id)}, 200

    @jwt_required
    def get(self):
        application_templates = ApplicationTemplate.objects().order_by('-timestamp')

        if 'excel' in request.args:
            return send_from_directory(directory=UPLOAD_FOLDER, filename=export_to_excel(application_templates, get_user_id()))

        return Response(application_templates.to_json(), mimetype="application/json", status=200)


class ApplicationTemplateApi(Resource):

    @jwt_required
    def get(self, id):
        return Response(ApplicationTemplate.objects.order_by('-timestamp').get(id=id).to_json(), mimetype="application/json", status=200)

    # TODO: Bringup DELETE Application Template API


class ApplicationsApi(Resource):

    @jwt_required
    def post(self):
        body = request.get_json()
        application = Application(**body).save()
        send_email_async(get_user_email(), 'notification', get_user_name(),
                         notif=f"Your Application has been successfully received for {application.name} and "
                               f"awaiting signatures from the authorities, Please check E-Daftar portal for more "
                               f"updates.")

        auth = User.objects.get(id=application.assignedId)
        send_email_async(auth.email, 'notification', auth.first_name,
                         notif=f"User {get_user_name()} has applied for {application.name} and is awaiting for your "
                               f"signatures, Please review it from the E-Daftar portal.")
        return {'id': str(application.id)}, 200

    @jwt_required
    def get(self):
        filter_q = None
        limit_q = None

        if 'filter' in request.args:
            if request.args['filter'] == 'signed':
                filter_q = Q(status=1)
            elif request.args['filter'] == 'rejected':
                filter_q = Q(status=-1)
            elif request.args['filter'] == 'pending':
                filter_q = Q(status=0)

        if 'limit' in request.args:
            limit_q = int(request.args['limit'])

        if get_jwt_identity()['role'] != 'user':
            if filter_q is not None:
                q = Application.objects(filter_q & (Q(assignedId=get_jwt_identity()['_id']['$oid']) |
                                                    Q(creatorId=get_jwt_identity()['_id']['$oid'])))
            else:
                q = Application.objects(Q(assignedId=get_jwt_identity()['_id']['$oid']) |
                                        Q(creatorId=get_jwt_identity()['_id']['$oid']))

        else:
            if filter_q is not None:
                q = Application.objects(filter_q & (Q(creatorId=get_jwt_identity()['_id']['$oid'])))
            else:
                q = Application.objects(Q(creatorId=get_jwt_identity()['_id']['$oid']))

        q = q.order_by('-timestamp')

        if 'excel' in request.args:
            return send_from_directory(directory=UPLOAD_FOLDER, filename=export_to_excel(q, get_user_id()))

        if limit_q is not None:
            return Response(q[:limit_q].to_json(), mimetype="application/json", status=200)
        else:
            return Response(q.to_json(), mimetype="application/json", status=200)


class ApplicationApi(Resource):

    @jwt_required
    def get(self, id):
        return Response(Application.objects(Q(id=id) & (Q(creatorId=get_jwt_identity()['_id']['$oid']) |
                                                        Q(assignedId=get_jwt_identity()['_id'][
                                                            '$oid']))).get().to_json(),
                        mimetype="application/json", status=200)

    @jwt_required
    def delete(self, id):
        Application.objects(Q(id=id) & Q(creatorId=get_jwt_identity()['_id']['$oid'])).delete()
        return '', 200


class SigningApi(Resource):

    @jwt_required
    @authority_required
    def post(self, id, action):
        body = request.get_json()

        if action == 'sign':
            return self.sign(id)
        elif action == 'reject':
            if body and 'message' in body:
                return self.reject(id, body['message'])
            else:
                return self.reject(id)

    def sign(self, id):
        application = Application.objects(Q(id=id) & Q(assignedId=get_jwt_identity()['_id']['$oid'])).get()

        if application.to_hash() != application.hash:
            return 'Data Tampered', 403

        current_stage = int(application.stage)
        private_key = User.objects(Q(id=get_jwt_identity()['_id']['$oid'])).get().private_key

        signatures = application.signatures
        signatures[current_stage] = Ecdsa.sign(json.dumps(application.to_hash()),
                                               PrivateKey.fromPem(private_key)).toBase64()

        application.update(signatures=signatures)

        if application.stage == application.stages - 1:
            application.update(stage=current_stage + 1)
            application.update(status=1)
        else:
            workflow = Workflow.objects(id=application.workflowId).get()
            new_auth_id = workflow.stages[current_stage + 1]['authId']
            new_auth_name = workflow.stages[current_stage + 1]['authName']
            application.update(assignedId=new_auth_id)
            application.update(assignedName=new_auth_name)
            application.update(stage=current_stage + 1)

        user = User.objects(Q(id=application.creatorId)).get()
        send_email_async(get_user_email(), 'notification', get_user_name(),
                         notif=f"You have successfully signed {application.name} created by {user.first_name} with "
                               f"your digital signatures")

        send_email_async(user.email, 'notification', user.first_name,
                         notif=f"{get_user_name()} has successfully signed your {application.name}. Please check "
                               f"E-Daftar portal for more updates.")

        return signatures[current_stage], 200

    def reject(self, id, message = None):
        application = Application.objects(Q(id=id) & Q(assignedId=get_jwt_identity()['_id']['$oid'])).get()

        if message is not None:
            application.update(message=message)

        application.update(status=-1)

        user = User.objects(Q(id=application.creatorId)).get()
        send_email_async(get_user_email(), 'notification', get_user_name(),
                         notif=f"You have successfully rejected {application.name} created by {user.first_name}.")

        send_email_async(get_user_email(), 'notification', get_user_name(),
                         notif=f"{get_user_name()} has unfortunately rejected your application due to the following "
                               f"reason: '{message}'. Please check E-Daftar portal for more updates.")

        return 'Success', 200
