import importlib
import os

import sentry_sdk
from flask import Flask
from flask_migrate import Migrate
from sentry_sdk.integrations.flask import FlaskIntegration

from app.common.exception import APIException
from app.common.logging import init_logging_config
from app.error_handler import exception_handler
from app.extensions import db, logger, jwt_manager
from app.jwt_callback import expired_token_callback, invalid_token_callback, unauthorized_callback, user_claims_callback
from app.routers import init_routers
from app.settings import setting


def get_addons():
    file_list = os.listdir('./app')
    dir_list = []
    for filename in file_list:
        if os.path.isdir(os.path.join('./app', filename)):
            dir_list.append(filename)
    return dir_list


def import_models():
    for addon in get_addons():
        module_path = f'app.{addon}.models'
        try:
            importlib.import_module(module_path)
        except ModuleNotFoundError:
            pass


def create_app():

    _app = Flask(__name__, static_folder='../static', template_folder='../templates')
    _app.config.from_object(setting)
    if setting.TESTING:
        _app.config['SQLALCHEMY_DATABASE_URI'] = f"test_{setting.SQLALCHEMY_DATABASE_URI}"

    db.app = _app
    db.init_app(_app)
    import_models()
    init_logging_config(_app)
    init_routers(_app)
    Migrate(_app, db)
    jwt_manager.init_app(_app)

    jwt_manager.expired_token_loader(expired_token_callback)
    jwt_manager.invalid_token_loader(invalid_token_callback)
    jwt_manager.unauthorized_loader(unauthorized_callback)
    jwt_manager.additional_claims_loader(user_claims_callback)

    # sentry_sdk.init(
    #     dsn=setting.SENTRY_URI,
    #     integrations=[FlaskIntegration()]
    # )
    if not os.path.exists(setting.ORIGIN_MEDIA_PATH):
        os.mkdir(setting.ORIGIN_MEDIA_PATH)
    if not os.path.exists(setting.ENCRYPT_MEDIA_PATH):
        os.mkdir(setting.ENCRYPT_MEDIA_PATH)

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
