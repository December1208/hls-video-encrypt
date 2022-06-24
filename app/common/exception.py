import json
from typing import Optional, Tuple

from flask import request
from werkzeug.exceptions import HTTPException


class Error:
    pass


class APIException(HTTPException):
    code = 200
    detail = 'sorry, we made a mistake!'
    error_code = 'A0000'

    def __init__(
            self, detail=None, error_code: Optional[str] = None, error: Optional[Tuple[str, str]] = None,
            extra_info=None
    ):
        if error:
            self.error_code = error[0]
            self.detail = error[1]
        if detail:
            self.detail = detail
        if error_code:
            self.error_code = error_code
        self.extra_info = extra_info

        super(APIException, self).__init__(detail, None)

    def get_body(self, environ=None, scope=None):
        body = dict(
            detail=self.detail,
            code=self.error_code,
            success=False,
            data=None,
            extra_info=self.extra_info,
        )
        text = json.dumps(body)
        return text

    def get_headers(self, environ=None, scope=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]
