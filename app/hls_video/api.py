import os
import uuid

from flask import Blueprint, request

from app.common import response
from app.settings import setting
import ipdb

video_api = Blueprint('video-api', __name__)


ALLOWED_EXTENSIONS = {'mp4'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@video_api.route('/video/upload', methods=['POST'])
def _upload():
    file = request.files['file']
    if file is None or not allowed_file(file.filename):
        return response.standard_response()

    file_uuid = uuid.uuid4().hex
    file_path = os.path.join(setting.ORIGIN_MEDIA_PATH, f"{file_uuid}.{file.filename.split('.')[-1]}")
    file.save(file_path)
    return response.standard_response()
