from app.hls_video.apis.hls_video_apis import video_api
from app.hls_video.views.hls_video_views import video_views


def init_routers(app):
    api = [
        video_api
    ]

    views = [
        video_views
    ]

    for api in api:
        app.register_blueprint(api, url_prefix=f'/api')

    for view in views:
        app.register_blueprint(view, url_prefix=f'/view')
