import importlib
from urllib.parse import urljoin

import m3u8
from flask_jwt_extended import create_access_token
from m3u8 import Playlist

from app.hls_video.constants import IndexType
from app.hls_video.models import HLSVideo
from app.settings import setting


class VideoService:

    @classmethod
    def get_video_public_url(cls, identity):
        token = create_access_token(identity=identity)

        public_url = urljoin(setting.SERVER_HOST, f'api/{identity}.m3u8') + f'?token={token}'
        return public_url

    @classmethod
    def parse_playlist_content(cls, hls_video: HLSVideo):
        if hls_video.index_type != IndexType.PLAYLIST:
            raise

        play_list = m3u8.loads(hls_video.content)
        for item in play_list.playlists:
            item: Playlist
            item.uri = cls.get_video_public_url(item.uri)

        return play_list.dumps()

    @classmethod
    def parse_segment_content(cls, hls_video: HLSVideo):
        if hls_video.index_type != IndexType.SEGMENT:
            raise

        return hls_video.content

    @classmethod
    def convert_mp4_to_hls(cls, file_identity):
        storage_backend = importlib.import_module(setting.STORAGE_BACKEND)
        backend = storage_backend(identity=file_identity)
