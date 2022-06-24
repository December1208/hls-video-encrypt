from flask_sqlalchemy import SQLAlchemy
from werkzeug.local import LocalProxy
from app.common.logging import get_log

db = SQLAlchemy()
logger = LocalProxy(get_log)
