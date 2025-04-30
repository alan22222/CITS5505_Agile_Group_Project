from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

class UploadedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    graph_path = db.Column(db.String(200), nullable=True)  # path to generated image
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)


class ModelRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    model_type = db.Column(db.String(50))
    precision_mode = db.Column(db.String(20))
    target_index = db.Column(db.Integer)
    has_header = db.Column(db.Boolean)
    result_json = db.Column(db.Text)
    graph_path = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
