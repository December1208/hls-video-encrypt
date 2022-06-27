from app.error_handler import error_response
from app.common.exception import Error


def expired_token_callback(_expired_jwt_header, _expired_jwt_data):

    return error_response(*Error.INVALID_TOKEN_ERROR)


def invalid_token_callback(error_string):

    return error_response(*Error.INVALID_TOKEN_ERROR)


def unauthorized_callback(error_string):

    return error_response(*Error.INVALID_TOKEN_ERROR)