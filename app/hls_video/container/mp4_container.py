import os

import bitstring
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

    def to_ts_segment(self, file_prefix, key: bytes, iv: bytes):
        # general ts segment and index file in the current directory

        outputs_cmd = constants.TS_FFMPEG_CMD
        index_file = os.path.join(self.save_path, f'{file_prefix}_index.m3u8')
        with open(os.path.join(self.save_path, 'enc.key'), 'wb') as f:
            f.write(key)
        with open(os.path.join(self.save_path, 'key.keyinfo'), 'w') as f:
            f.writelines(
                [f"url\n", f"{os.path.join(self.save_path, 'enc.key')}\n", iv.hex()]
            )

        outputs_cmd.extend([
            "-hls_key_info_file", os.path.join(self.save_path, 'key.keyinfo')
        ])
        outputs_cmd.extend([
            '-hls_segment_filename', f"{os.path.join(self.save_path, file_prefix)}%d.ts"
        ])
        ff = ffmpy.FFmpeg(
            inputs={self.filename: None},
            outputs={index_file: outputs_cmd}
        )
        ff.run()
        return index_file

    def multi_bit_rate_to_ts_segment(self, file_prefix, key: bytes, iv: bytes):
        outputs_cmd = constants.MULTI_BIT_RATE_TS_FFMPEG_CMD
        master_file = os.path.join(self.save_path, 'master.m3u8')
        index_file = os.path.join(self.save_path, f'{file_prefix}_%v.m3u8')
        with open(os.path.join(self.save_path, 'enc.key'), 'wb') as f:
            f.write(key)
        with open(os.path.join(self.save_path, 'key.keyinfo'), 'w') as f:
            f.writelines(
                [f"url\n", f"{os.path.join(self.save_path, 'enc.key')}\n", iv.hex()]
            )

        outputs_cmd.extend([
            "-hls_key_info_file", os.path.join(self.save_path, 'key.keyinfo'), '-master_pl_name', master_file
        ])
        ff = ffmpy.FFmpeg(
            inputs={self.filename: None},
            outputs={index_file: outputs_cmd}
        )
        ff.run()

        return os.path.join(self.save_path, master_file)
