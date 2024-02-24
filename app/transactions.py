from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from models import db, Transaction
from flask import Blueprint, jsonify
from datetime import datetime
from flask import request, redirect, flash, jsonify
from flask_login import current_user
from models import db, User, Transaction
import locale
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity


transactions_bp = Blueprint('transactions_bp', __name__)


@transactions_bp.route('/cash_transfer/<int:receiver_id>/<float:amount>', methods=['POST'])
@jwt_required()
def cash_transfer(receiver_id, amount):
    current_user_id = get_jwt_identity()
    sender = current_user.id

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
@jwt_required()
def deposit():
    data = request.get_json()

    amount = data.get('amount')
    memo = data.get('memo')

    if not amount or float(amount) <= 0:
        return jsonify({'error': 'Invalid amount'}), 400

    current_user.balance += float(amount)

    new_transaction = Transaction(
        user=current_user, type='deposit', amount=float(amount), memo=memo)
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({'message': f'Successful Deposit of {locale.currency(float(amount), grouping=True)} at {datetime.now().strftime("%Y-%m-%d %I:%M %p")}'})


@transactions_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    data = request.get_json()

    amount = data.get('amount')
    memo = data.get('memo')

    if not amount or float(amount) <= 0:
        return jsonify({'error': 'Invalid amount'}), 400

    if current_user.balance < float(amount):
        return jsonify({'error': 'Insufficient balance for withdrawal'})

    current_user.balance -= float(amount)

    new_transaction = Transaction(
        user=current_user, type='withdraw', amount=float(amount), memo=memo)
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({'message': f'Successful Withdrawal of {locale.currency(float(amount), grouping=True)} at {datetime.now().strftime("%Y-%m-%d %I:%M %p")}'})
