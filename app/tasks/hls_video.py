import os


from app.hls_video.container.mp4_container import MP4Container
from asynctask.app import celery


@celery.task
def convert_mp4_to_m3u(identity, file_path):
    key = os.urandom(16)
    iv = os.urandom(16)
    mp4_container = MP4Container(identity, filename=file_path)
    file_prefix = os.urandom(8).hex()
    ts_index_file = mp4_container.multi_bit_rate_to_ts_segment(file_prefix=file_prefix, key=key, iv=iv)
