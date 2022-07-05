import os
from urllib.parse import urljoin

import m3u8
from flask_jwt_extended import create_access_token, decode_token
from m3u8 import Playlist, Key, Segment
from werkzeug.exceptions import NotFound

from app.settings import setting
from app.util.aes_crypt import AESCrypt


class VideoService:

    @classmethod
    def get_video_public_uri(cls, identity, filename, token, only_token=True):
        public_uri = f"{filename}?token={token}"

        if not only_token:
            public_uri = f"/api/video/{identity}/{public_uri}"
        return public_uri

    @classmethod
    def get_video_static_uri(cls, identity, filename):
        static_uri = urljoin(setting.SERVER_HOST, f'/{setting.ENCRYPT_MEDIA_PATH}/{identity}/{filename}')
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
    def parse_key_info(cls, identity, filename, token):
        payload = decode_token(token)
        key, iv = payload['key'], payload['iv']
        file_path = os.path.join(setting.ENCRYPT_MEDIA_PATH, identity, filename)
        with open(file_path, 'rb') as f:
            data = f.read()
        aes_crypt = AESCrypt(key=bytes.fromhex(key), iv=bytes.fromhex(iv))
        result = aes_crypt.encrypt(data)
        return result
