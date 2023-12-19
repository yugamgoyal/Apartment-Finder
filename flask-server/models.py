from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime, timedelta
import hashlib
import os


db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

def generate_verification_token(email):
    salt = os.urandom(16)
    return hashlib.sha256(salt + email.encode()).hexdigest()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)
    verified = db.Column(db.Boolean)
    verify_token = db.Column(db.String(64), unique=True)
    expiration_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    # TODO: [AF-1] Add any other colums/options we want to track
    
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name 
        self.last_name = last_name 
        self.email = email
        self.password = password
        self.verified = False
        self.verify_token = generate_verification_token(email)