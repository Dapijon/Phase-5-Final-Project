from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_login import current_user
from .models import db, User, Transaction
import locale
from flask_jwt_extended import jwt_required, get_jwt_identity

transactions_bp = Blueprint('transactions_bp', __name__)

@transactions_bp.route('/cash_transfer/<int:receiver_id>/<float:amount>', methods=['POST'])
@jwt_required()
def cash_transfer(receiver_id, amount):
    sender = User.query.get(get_jwt_identity())

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'})

    try:
        if sender.balance >= Decimal(amount):
            sender.balance -= Decimal(amount)
            receiver = User.query.get(receiver_id)
            receiver.balance += Decimal(amount)

            new_transaction = Transaction(
                sender=sender, receiver=receiver, amount=Decimal(amount))
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

    return jsonify({'message': f'Successful Deposit of {locale.currency(float(amount), grouping=True)} at {datetime.now().strftime("%Y-%m-%d %I:%M %p")}'})
