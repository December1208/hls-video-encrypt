import importlib
import os
import uuid
from typing import Optional

from flask import Blueprint, request, render_template
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import NotFound

from app.common import response
from app.extensions import db
from app.hls_video.constants import IndexType
from app.hls_video.models import HLSVideo
from app.hls_video.service import VideoService
from app.settings import setting
from flask_jwt_extended.utils import get_jti
from app.util.aes_crypt import AESCrypt
from flask_jwt_extended import create_access_token
from tempfile import NamedTemporaryFile


video_api = Blueprint('video-api', __name__)


ALLOWED_EXTENSIONS = {'mp4'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@video_api.route('/video/upload', methods=['POST'])
def _upload():
    from app.tasks import hls_video

    file = request.files['file']
    if file is None or not allowed_file(file.filename):
        return response.standard_response()

    identity = uuid.uuid4().hex
    file_path = os.path.join(setting.ORIGIN_MEDIA_PATH, f"{identity}.{file.filename.split('.')[-1]}")
    file.save(file_path)
    hls_video.convert_mp4_to_m3u.delay(identity, file_path)
    return response.standard_response()


@video_api.route('/video/<string:identity>.m3u8', methods=['GET'])
@jwt_required()
def _get_video_content(identity):

    hls_video: Optional[HLSVideo] = db.session.query(HLSVideo).filter(HLSVideo.uuid == identity).first()
    if hls_video is None:
        raise NotFound
    if hls_video.index_type == IndexType.PLAYLIST:
        result = VideoService.parse_playlist_content(hls_video)
    elif hls_video.index_type == IndexType.SEGMENT:
        result = VideoService.parse_segment_content(hls_video)
    else:
        raise NotFound

    return response.standard_txt_response(result)


@video_api.route('/video/<string:identity>/<string:file_name>', methods=['GET'])
@jwt_required()
def _get_video_key(identity, file_name):
    params = request.args.to_dict()
    token = params['token']

    # hls_video: Optional[HLSVideo] = db.session.query(HLSVideo).filter(HLSVideo.uuid == identity).first()
    # if hls_video is None:
    #     raise NotFound

    jti = get_jti(token)
    jti = jti.replace('-', '')
    # iv = os.urandom(16)
    iv = b'av\xba\x14&\x01\x953\x8fR\xbd\xb6\xd5\xbb\xdb4'
    print(iv.hex())
    # iv = "d354f157e301478e1224e846883a6aff"
    # print(jti, iv.hex())
    # key, iv = hls_video.key, hls_video.iv
    file = 'static/encrypt_media/f1eb13ba437746ca9098ac8630f73689/test.key'
    with open(file, 'rb') as f:
        data = f.read()
    aes_crypt = AESCrypt(key=bytes.fromhex(jti), iv=iv)
    result = aes_crypt.encrypt(data)
    return response.standard_txt_response(result)


@video_api.route('/video/', methods=['POST'])
def _update_jwt():
    return response.standard_txt_response(create_access_token("123"))


@video_api.route('/video/origin-demo/', methods=['GET'])
def _origin_demo():
    return render_template('origin_demo.html')


@video_api.route('/video/encrypt-demo/', methods=['GET'])
def _encrypt_demo():
    return render_template('encrypt_demo.html')
