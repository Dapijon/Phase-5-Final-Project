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
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'dob': self.dob.strftime('%Y-%m-%d %H:%M:%S') if self.dob else None,
            'email': self.email,
            'national_ID': self.national_ID,
            'phoneNumber': self.phoneNumber,
           
            'balance': self.balance,
            
            'favorites': [favorite.to_dict() for favorite in self.favorites],
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }

    def __repr__(self):
        return f'<User {self.id} - {self.first_name} {self.last_name}>'


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
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat(),
            'sender': self.sender.to_dict() if self.sender else None,
            'receiver': self.receiver.to_dict() if self.receiver else None,
        }
    
    def __repr__(self):
        return f'<Transaction {self.id} from {self.sender_id} to {self.receiver_id} for {self.amount}>'


