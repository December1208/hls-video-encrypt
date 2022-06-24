import importlib
import os

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

# from apps.api import Api
from app.common.logging import init_logging_config
from app.error_handler import exception_handler
from app.foundation import db, jwt, cache
from apps.jwt_callbacks import expired_token_callback, invalid_token_callback, user_lookup_callback, \
    verify_jwt_in_request, unauthorized_callback
from apps.middleware import Middleware
from apps.settings import setting
from flask_jwt_extended import view_decorators


def get_addons():
    file_list = os.listdir('./apps')
    dir_list = []
    for filename in file_list:
        if os.path.isdir(os.path.join('./apps', filename)):
            dir_list.append(filename)
    return dir_list


def import_models():
    for addon in get_addons():
        module_path = f'apps.{addon}.models'
        try:
            importlib.import_module(module_path)
        except ModuleNotFoundError:
            print(f"Not found {addon}")


def create_app():

    _app = Flask(__name__)
    _app.config.from_object(setting)
    if setting.TESTING:
        _app.config['SQLALCHEMY_DATABASE_URI'] = setting.TEST_SQLALCHEMY_DATABASE_URI
        _app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        _app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10, 'pool_recycle': 120
        }

    db.app = _app
    db.init_app(_app)

    cache.init_app(_app)

    init_logging_config(_app)

    Api(_app)

    jwt.init_app(_app)
    jwt.expired_token_loader(expired_token_callback)
    jwt.invalid_token_loader(invalid_token_callback)
    jwt.user_lookup_loader(user_lookup_callback)
    jwt.unauthorized_loader(unauthorized_callback)
    view_decorators.verify_jwt_in_request = verify_jwt_in_request

    Middleware(_app)

    sentry_sdk.init(
        dsn=setting.SENTRY_URI,
        integrations=[FlaskIntegration()]
    )

    @_app.errorhandler(Exception)
    def errorhandler(e):
        # raise APIException 不会rollback？
        db.session.rollback()
        return exception_handler(e)

    @_app.teardown_appcontext
    def release_db(response):
        db.session.close()
        return response

    return _app


app = create_app()
