from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        dob=datetime.strptime(data['dob'], '%Y-%m-%d'),
        email=data['email'],
        national_ID=data['national_ID'],
        phoneNumber=data['phoneNumber'],
        password=data['password'],
        transaction_password=data['transaction_password']
    )
    db.session.add(new_user)
    db.session.commit()
    
    
    return jsonify({'message': 'User created successfully'})

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    # if user and check_password_hash(user.password, data['password']):
    if user and  data['password']:
        login_user(user)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

        # return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@auth.route('/logout')
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})

