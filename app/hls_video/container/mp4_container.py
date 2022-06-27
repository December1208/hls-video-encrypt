import bitstring
import os

import ffmpy

from app.hls_video import constants
from app.settings import setting


class MP4Container:
    container_type = constants.ContainerType.MP4

    def __init__(self, identity, filename=None, bytes_input=None, offset_bytes=0):
        self.identity = identity

        if filename:
            self.bs = bitstring.ConstBitStream(filename=filename, offset=offset_bytes * 8)
        elif bytes_input:
            self.bs = bitstring.ConstBitStream(bytes=bytes_input, offset=offset_bytes * 8)

        self.filename = filename
        self.save_path = os.path.join(setting.ENCRYPT_MEDIA_PATH, self.identity)
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

    def to_flv_segment(self, video_resolution, file_prefix, index_file_type=constants.ContainerType.M3U8):
        # general flv segment and index file in the current directory

        index_file = os.path.join(self.save_path, f"{file_prefix}.{index_file_type}")
        flv_file_path = os.path.join(
            self.save_path, f'{file_prefix}d%_{video_resolution}.{constants.ContainerType.FLV}'
        )

        outputs_cmd = constants.FLV_SHARPNESS_TYPE_TO_FFMPEG_CMD[video_resolution]
        outputs_cmd.extend(['-segment_list', index_file])
        ff = ffmpy.FFmpeg(
            inputs={self.filename: None},
            outputs={flv_file_path: outputs_cmd}
        )
        ff.run()
        return index_file

    def to_ts_segment(self, file_prefix, key, iv):
        # general ts segment and index file in the current directory

        outputs_cmd = constants.TS_FFMPEG_CMD
        master_file = f'{file_prefix}_master.m3u8'
        index_file = os.path.join(self.save_path, f'{file_prefix}%v.m3u8')

        outputs_cmd.extend([index_file, '-master_pl_name', master_file, '-master_pl_name', master_file])
        outputs_cmd.extend([
            "-hls_enc_key", key, '-hls_enc_key_url', "url", "-hls_enc_iv", iv
        ])

        outputs_cmd.extend([
            '-hls_segment_filename', f"{os.path.join(self.save_path, file_prefix)}%d.ts",
        ])
        ff = ffmpy.FFmpeg(
            inputs={self.filename: None},
            outputs={index_file: outputs_cmd}
        )
        ff.run()
        return index_file
