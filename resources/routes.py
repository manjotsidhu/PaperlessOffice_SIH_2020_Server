from resources.form import SaveFormApi, GetFormApi
from resources.index import IndexApi
from .user import UsersApi, UserApi
from .auth import SignupApi, LoginApi


def initialize_routes(api):
    api.add_resource(IndexApi, '/')
    api.add_resource(UsersApi, '/users')
    api.add_resource(UserApi, '/user')
    api.add_resource(SignupApi, '/auth/signup')
    api.add_resource(LoginApi, '/auth/login')
    api.add_resource(SaveFormApi, '/form')
    api.add_resource(GetFormApi, '/form/<string:id>')
