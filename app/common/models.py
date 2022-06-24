from apps.foundation import db


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    __app_label__ = ""
    __model__ = ""
    __tablename__ = f"{__app_label__}_{__model__}"


class Likable(BaseModel):
    __abstract__ = True

    like_count = db.Column(db.Integer, doc="点赞数", default=0, nullable=False)
    fake_like_count = db.Column(db.Integer, doc="假点赞数", default=0)


class Commentable(BaseModel):
    __abstract__ = True

    comment_count = db.Column(db.Integer, doc="评论数", default=0, nullable=False)
