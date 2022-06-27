from flask_sqlalchemy import SQLAlchemy
from werkzeug.local import LocalProxy
from app.common.logging import get_log
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
logger = LocalProxy(get_log)
jwt_manager = JWTManager()
