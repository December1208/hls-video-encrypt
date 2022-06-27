from app.hls_video.apis.public_api import video_api


def init_routers(app):
    api = [
        video_api
    ]

    for api in api:
        app.register_blueprint(api, url_prefix=f'/api')
