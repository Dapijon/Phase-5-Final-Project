from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db= SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    national_ID = db.Column(db.String, nullable=False, unique=True)
    phoneNumber = db.Column(db.String, nullable=False, unique=True)
    password= db.Column(db.String, nullable= False)
    balance = db.Column(db.Float, default=0)
    transaction_password = db.Column(db.Integer, nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, server_default='0')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Favorite(db.Model):
    
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    favorite_user_id = db.Column(db.Integer, nullable=False)
    
class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id= db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])


