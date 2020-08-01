from resources.application import ApplicationsApi, ApplicationApi, SigningApi, ApplicationsTemplateApi, \
    ApplicationTemplateApi
from resources.form import FormApi, GetFormApi
from resources.index import IndexApi
from resources.scan import ScanApi
from resources.settings import UserSettingsApi, UserSettingsPostApi
from resources.storage import StorageApi, UserStorageApi
from resources.workflow import WorkflowApi, WorkFlowByIdApi
from .user import UsersApi, UserApi
from .auth import SignupApi, LoginApi, LogoutApi


def initialize_routes(api):
    api.add_resource(IndexApi, '/')
    api.add_resource(ScanApi, '/scanner')
    api.add_resource(UsersApi, '/users')
    api.add_resource(UserApi, '/user')
    api.add_resource(SignupApi, '/auth/signup')
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(LogoutApi, '/auth/logout')
    api.add_resource(FormApi, '/form')
    api.add_resource(GetFormApi, '/form/<string:id>')
    api.add_resource(WorkflowApi, '/workflow')
    api.add_resource(WorkFlowByIdApi, '/workflow/<string:id>')
    api.add_resource(ApplicationsApi, '/applications')
    api.add_resource(ApplicationsTemplateApi, '/applications/templates')
    api.add_resource(ApplicationTemplateApi, '/applications/templates/<string:id>')
    api.add_resource(ApplicationApi, '/applications/<string:id>')
    api.add_resource(SigningApi, '/applications/<string:id>/<string:action>')
    api.add_resource(StorageApi, '/storage')
    api.add_resource(UserStorageApi, '/storage/<string:doc_id>')
    api.add_resource(UserSettingsApi, '/settings/<string:key>')
    api.add_resource(UserSettingsPostApi, '/settings/<string:key>/<string:value>')
