from flask import Blueprint, request

from app.common import response
from app.hls_video.service import VideoService

inner_video_api = Blueprint('inner-video-api', __name__)


@inner_video_api.route('/video/public-url', methods=['POST'])
def _get_public_url():
    req_data = request.get_json() or []

    result = []
    for item in req_data:
        result.append({
            'identity': item['identity'],
            'url': VideoService.get_video_public_url(item['identity'])
        })

    return response.standard_response(result)
