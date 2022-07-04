class IndexType:
    PLAYLIST = 'playlist'
    SEGMENT = "segment"


class ContainerType:
    TS = 'ts'
    FLV = 'flv'
    MP4 = 'mp4'
    M3U8 = 'm3u8'
    JSON = 'json'
    KEY = 'key'


class VideoResolution:
    LD = 'ld'  # 480P
    SD = 'sd'  # 720P
    HD = 'hd'  # 1080P


FLV_SHARPNESS_TYPE_TO_FFMPEG_CMD = {
    VideoResolution.LD: ['-s', '720x480', '-c:v', 'libx264', '-c:a', 'aac', '-flvflags', 'add_keyframe_index', '-f', 'segment', '-segment_format', 'flv', '-reset_timestamps', '1', '-segment_list_type', 'csv'],
    VideoResolution.SD: ['-s', '1280x720', '-c:v', 'libx264', '-c:a', 'aac', '-flvflags', 'add_keyframe_index', '-f', 'segment', '-segment_format', 'flv', '-reset_timestamps', '1', '-segment_list_type', 'csv'],
    VideoResolution.HD: ['-s', '1920x1080', '-c:v', 'libx264', '-c:a', 'aac', '-flvflags', 'add_keyframe_index', '-f', 'segment', '-segment_format', 'flv', '-reset_timestamps', '1', '-segment_list_type', 'csv']
}

TS_RESOLUTION_TYPE_TO_FFMPEG_CMD = {
    VideoResolution.LD: ['-s', '720x480', '-c:v', 'libx264', '-c:a', 'aac', '-hls_time', '10', '-hls_playlist_type', 'vod'],
    VideoResolution.SD: ['-s', '1280x720', '-c:v', 'libx264', '-c:a', 'aac', '-hls_time', '10', '-hls_playlist_type', 'vod'],
    VideoResolution.HD: ['-s', '1920x1080', '-c:v', 'libx264', '-c:a', 'aac', '-hls_time', '10', '-hls_playlist_type', 'vod']
}


# 多码率生成TS，命令有点问题
MULTI_BIT_RATE_TS_FFMPEG_CMD = [
    '-s:0', '1920x1080', '-c:v', 'libx264', '-b:v:0', '6000k', '-c:a', 'aac', '-b:a:0', '128k',
    '-s:2', '1280x720', '-c:v', 'libx264', '-b:v:1', '2000k', '-c:a', 'aac', '-b:a:1', '128k',
    '-s:4', '720x480', '-c:v', 'libx264', '-b:v:2', '800k', '-c:a', 'aac', '-b:a:2', '128k',
    '-map', '0:v', '-map', '0:a', '-map', '0:v', '-map', '0:a', '-map', '0:v', '-map', '0:a', '-f', 'hls',
    '-hls_time', '180', '-hls_list_size', '0', '-hls_playlist_type', 'vod', '-var_stream_map', 'v:0,a:0 v:1,a:1 v:2,a:2',
]

# 只转TS
TS_FFMPEG_CMD = [
    '-f', 'hls', '-hls_time', '60', '-hls_list_size', '0', '-hls_playlist_type', 'vod'
]
