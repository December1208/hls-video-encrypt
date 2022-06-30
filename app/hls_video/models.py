from app.common.models import BaseModel
from app.extensions import db


class HLSVideo(BaseModel):
    filename = db.Column(db.String(128), doc="上传时的文件名")
    identity = db.Column(db.String(32), index=True, nullable=False, doc="文件唯一标识")
    origin_file_path = db.Column(db.Text, doc="加密前文件地址")
    file_path = db.Column(db.Text, doc="加密后文件地址")

    transcoding_finished = db.Column(db.Boolean, default=False, doc="是否转码完成")
    key = db.Column(db.String(32), doc="加密所用秘钥")
    iv = db.Column(db.String(32), doc="加密所用iv")
