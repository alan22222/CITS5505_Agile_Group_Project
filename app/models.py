from datetime import datetime

from app import db
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

class UploadedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    upload_date =  db.Column(db.DateTime, default=datetime.utcnow)  # file creation time
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



class ModelRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # CSV file selected
    model_type = db.Column(db.String(50), nullable=False)  # e.g., 'lr', 'knn'
    precision_mode = db.Column(db.String(50), nullable=False)  # e.g., 'fast', 'balanced', 'accurate'
    target_index = db.Column(db.Integer, nullable=False)  # Index of target column
    has_header = db.Column(db.Boolean, default=True)  # If CSV has a header
    created_at = db.Column(db.DateTime, nullable=False)  # file creation time
    result_json = db.Column(db.Text)  # Store output metrics as JSON (if needed)
    graph_path = db.Column(db.String(255))  # Path to the saved chart image (if any)


class SharedResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    modelrun_id = db.Column(db.Integer, db.ForeignKey('model_run.id'), nullable=False)

    shared_at = db.Column(db.DateTime, default=datetime.utcnow)
    result_snapshot = db.Column(db.Text, nullable=False)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_shares')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_shares')
    modelrun = db.relationship('ModelRun', backref='shared_records')


