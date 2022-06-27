import traceback

from flask import jsonify

from app.common.exception import APIException
from app.extensions import logger


def error_response(error_code, detail):

    response_data = {
        'code': error_code,
        'data': None,
        'success': False,
        'detail': detail
    }

    return jsonify(response_data), 200


def exception_handler(e):

    # sentry_sdk.capture_exception(e)
    if isinstance(e, APIException):
        # 截取最后512个字符
        msg = traceback.format_exc()
        logger.info(msg[-512:])
        return e
    return e
