from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from flask import Blueprint, jsonify
from datetime import datetime
from flask import request, redirect, flash, jsonify
from flask_login import current_user
from .models import db, User, Transaction
import locale
from flask_jwt_extended import jwt_required, get_jwt_identity


transactions_bp = Blueprint('transactions_bp', __name__)


@transactions_bp.route('/cash_transfer/<int:receiver_id>/<float:amount>', methods=['POST'])
@jwt_required()
def cash_transfer(receiver_id, amount):
    current_user = get_jwt_identity()
    sender = current_user

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'})

    try:
        if current_user.balance >= Decimal(amount):
            current_user.balance -= Decimal(amount)
            receiver = User.query.get(receiver_id)
            receiver.balance += Decimal(amount)

            new_transaction = Transaction(
                sender=current_user, receiver=receiver, amount=Decimal(amount))
            db.session.add(new_transaction)

            db.session.commit()

            return jsonify({'message': 'Transaction successful'})
        else:
            return jsonify({'error': 'Insufficient funds'})
    except SQLAlchemyError as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f"Error: {str(e)}"})


@transactions_bp.route('/deposit', methods=['POST'])
# @jwt_required()
def deposit():
    data = request.get_json()

    amount = data.get('amount')
    memo = data.get('memo')
    id = data.get('id')
    user = User.query.filter(User.id == id).first()

    if not amount or float(amount) <= 0:
        return jsonify({'error': 'Invalid amount'}), 400

    # current_user.balance += float(amount)
    user.balance += float(amount)

    new_transaction = Transaction(
        sender_id=id, receiver_id=id, amount=float(amount))
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({'message': f'Successful Deposit of {float(amount)} '})





@transactions_bp.route('/send', methods=['POST'])  # Ensure this route accepts POST requests
def sendMoney():
    data = request.get_json()
    sender_id = data.get('sender')
    receiver_id = data.get('receiver')
    amount = float(data.get('amount'))

    sender = User.query.filter(User.id == sender_id).first()
    receiver = User.query.filter(User.id == receiver_id).first()

    if not receiver:
        return jsonify({'error': 'Receiver user does not exist'}), 404

    if not sender:
        return jsonify({'error': 'Sender user does not exist'}), 404

    # if sender.balance < amount:
    #     return jsonify({'error': 'Insufficient balance'}), 400

    # sender.balance -= amount
    # receiver.balance += amount

    transaction = Transaction(sender_id=sender_id, receiver_id=receiver_id, amount=amount)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({'message': 'Money sent'}), 201

    