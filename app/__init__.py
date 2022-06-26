import importlib
import os
import traceback

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

from app.common.exception import APIException
from app.common.logging import init_logging_config
from app.extensions import db, logger
from app.routers import init_routers
from app.settings import setting


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
        _app.config['SQLALCHEMY_DATABASE_URI'] = f"test_{setting.SQLALCHEMY_DATABASE_URI}"

    db.app = _app
    db.init_app(_app)
    init_logging_config(_app)
    init_routers(_app)

    sentry_sdk.init(
        dsn=setting.SENTRY_URI,
        integrations=[FlaskIntegration()]
    )
    if not os.path.exists(setting.ORIGIN_MEDIA_PATH):
        os.mkdir(setting.ORIGIN_MEDIA_PATH)
    if not os.path.exists(setting.ENCRYPT_MEDIA_PATH):
        os.mkdir(setting.ENCRYPT_MEDIA_PATH)

    @_app.errorhandler(Exception)
    def errorhandler(e):
        # raise APIException 不会rollback？
        db.session.rollback()

        if isinstance(e, APIException):
            # 截取最后512个字符
            msg = traceback.format_exc()
            logger.info(msg[-512:])
        return e

    @_app.teardown_appcontext
    def release_db(response):
        # db.session.close()
        return response

    return _app


app = create_app()
