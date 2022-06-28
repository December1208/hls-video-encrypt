from app.common.models import BaseModel
from app.extensions import db


class HLSVideo(BaseModel):
    identity = db.Column(db.String(32), index=True, nullable=False, doc="文件唯一标识")
    content = db.Column(db.Text, doc="文件内容")
    index_type = db.Column(db.String(32), doc="索引文件类型")
    origin_file_path = db.Column(db.Text, doc="加密前文件地址")
    file_path = db.Column(db.Text, doc="加密后文件地址")

    transcoding_finished = db.Column(db.Boolean, default=False, doc="是否转码完成")
    key = db.Column(db.String(32), doc="加密所用秘钥")
    iv = db.Column(db.String(32), doc="加密所用iv")
