import os
from typing import Optional

import ffmpy

from app.extensions import logger, db
from app.hls_video.container import MP4Container
from app.hls_video.models import HLSVideo
from asynctask.asynctask import async_task


@async_task
def convert_mp4_to_m3u(identity, file_path):
    key = os.urandom(16)
    iv = os.urandom(16)
    hls_video: Optional[HLSVideo] = db.session.query(HLSVideo).filter(HLSVideo.identity == identity).first()
    if hls_video is None:
        return
    hls_video.key, hls_video.iv = key.hex(), iv.hex()
    mp4_container = MP4Container(identity, filename=file_path)
    file_prefix = os.urandom(8).hex()
    try:
        ts_index_file = mp4_container.multi_bit_rate_to_ts_segment(file_prefix=file_prefix, key=key, iv=iv)
    except ffmpy.FFRuntimeError as e:
        logger.error(str(e))
    else:
        hls_video.transcoding_finished = True
        hls_video.file_path = ts_index_file

    db.session.commit()
