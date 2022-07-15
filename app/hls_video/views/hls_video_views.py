from typing import Optional

from flask import Blueprint, request, render_template
from flask_jwt_extended import create_access_token
from werkzeug.exceptions import NotFound

from app.extensions import db
from app.hls_video.models import HLSVideo
from app.hls_video.service import VideoService

video_views = Blueprint('video-view-api', __name__)


@video_views.route('/video/encrypt-demo', methods=['GET'])
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


@video_views.route('/video/upload', methods=['GET'])
def _upload_template():
    return render_template('upload.html')


@video_views.route('/video-list/', methods=['GET'])
def _video_list():
    queryset = db.session.query(HLSVideo).order_by(HLSVideo.id.desc())
    result = [
        {"name": item.filename, "url": f"/view/video/encrypt-demo?identity={item.identity}", 'transcoding_finished': item.transcoding_finished}
        for item in queryset
    ]
    return render_template('video_list.html', video_list=result)


@video_views.route('/video/origin-demo', methods=['GET'])
def _origin_demo():
    return render_template('origin_demo.html')
