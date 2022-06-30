import os
from urllib.parse import urljoin

import m3u8
from flask_jwt_extended import create_access_token
from m3u8 import Playlist, Key, Segment
from werkzeug.exceptions import NotFound

from app.hls_video.constants import IndexType
from app.hls_video.models import HLSVideo
from app.settings import setting


class VideoService:

    @classmethod
    def get_video_public_uri(cls, identity, filename, token):

        public_uri = urljoin(setting.SERVER_HOST, f'api/video/{identity}/{filename}') + f'?token={token}'
        return public_uri

    @classmethod
    def get_video_static_uri(cls, identity, filename):
        static_uri = urljoin(setting.SERVER_HOST, f'/static/{filename}')
        return static_uri

    @classmethod
    def parse_playlist_content(cls, identity, filename):
        token = create_access_token(identity=identity)

        file_path = os.path.join(setting.ENCRYPT_MEDIA_PATH, identity, filename)
        if not os.path.exists(file_path):
            raise NotFound
        with open(file_path) as f:
            content = f.read()

        play_list = m3u8.loads(content)
        for item in play_list.playlists:
            item: Playlist
            item.uri = cls.get_video_public_uri(identity, item.uri, token)

        for item in play_list.keys:
            item: Key
            item.uri = cls.get_video_public_uri(identity, item.uri, token)

        for item in play_list.segments:
            item: Segment
            item.uri = cls.get_video_static_uri(identity, item.uri)

        return play_list.dumps()

    @classmethod
    def parse_segment_content(cls, hls_video: HLSVideo):
        if hls_video.index_type != IndexType.SEGMENT:
            raise
        play_list = m3u8.loads(hls_video)
        return hls_video.content
