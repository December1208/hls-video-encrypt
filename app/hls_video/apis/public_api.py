import os
import uuid
from typing import Optional

from flask import Blueprint, request, render_template
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import NotFound

from app.common import response
from app.extensions import db
from app.hls_video.constants import ContainerType
from app.hls_video.models import HLSVideo
from app.hls_video.service import VideoService
from app.settings import setting
from multiprocessing import Process


video_api = Blueprint('video-api', __name__)


ALLOWED_EXTENSIONS = {'mp4'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@video_api.route('/video/upload', methods=['POST'])
def _upload():
    # from app.tasks import hls_video as hls_video_tasks
    from app.async_task.hls_video import convert_mp4_to_m3u

    file = request.files['file']
    if file is None or not allowed_file(file.filename):
        return response.standard_response()

    identity = uuid.uuid4().hex
    file_path = os.path.join(setting.ORIGIN_MEDIA_PATH, f"{identity}.{file.filename.split('.')[-1]}")
    file.save(file_path)
    hls_video_ins = HLSVideo(
        identity=identity,
        origin_file_path=f"{identity}.{file.filename.split('.')[-1]}",
        filename=file.filename,
    )
    db.session.add(hls_video_ins)
    db.session.commit()
    # hls_video_tasks.convert_mp4_to_m3u.delay(identity, file_path)
    p = Process(target=convert_mp4_to_m3u, args=(identity, file_path))
    p.start()
    # p.join()
    # asyncio.run(convert_mp4_to_m3u(identity, file_path))
    return response.standard_response()


@video_api.route('/video/<string:identity>/<string:filename>', methods=['GET'])
@jwt_required()
def _get_video_content(identity, filename):
    params = request.args.to_dict()
    print(filename)
    if filename.endswith(ContainerType.M3U8):
        hls_video: Optional[HLSVideo] = db.session.query(HLSVideo).filter(HLSVideo.identity == identity).first()
        if hls_video is None:
            print('not found')
            raise NotFound
        result = VideoService.parse_playlist_content(identity, filename)
    elif filename.endswith(ContainerType.KEY):
        token = params['token']
        result = VideoService.parse_key_info(identity, filename, token)
    else:
        print('not found 2')
        raise NotFound

    return response.standard_txt_response(result)


@video_api.route('/video/origin-demo', methods=['GET'])
def _origin_demo():
    return render_template('origin_demo.html')


@video_api.route('/video/encrypt-demo', methods=['GET'])
def _encrypt_demo():
    params = request.args.to_dict()
    identity = params.get('identity')
    hls_video: Optional[HLSVideo] = db.session.query(HLSVideo).filter(HLSVideo.identity == identity).first()
    if hls_video is None:
        raise NotFound

    token = create_access_token(identity=identity)
    public_uri = VideoService.get_video_public_uri(identity, hls_video.file_path, token, False)
    public_uri = request.host_url.strip('/') + public_uri
    return render_template('encrypt_demo.html', video_url=public_uri)


@video_api.route('/video/upload', methods=['GET'])
def _upload_template():
    return render_template('upload.html')


@video_api.route('/video-list/', methods=['GET'])
def _video_list():
    queryset = db.session.query(HLSVideo).filter(
        HLSVideo.transcoding_finished.is_(True)
    ).order_by(HLSVideo.id.desc())
    result = [
        {"name": item.filename, "url": f"/api/video/encrypt-demo?identity={item.identity}"}
        for item in queryset
    ]
    return render_template('video_list.html', video_list=result)
