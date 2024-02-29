from datetime import datetime
import requests
import base64
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Flask, Blueprint, jsonify, request
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError
from .models import db, User, Transaction

app = Flask(__name__)

transactions_bp = Blueprint('transactions_bp', __name__)


@transactions_bp.route('/process_payment', methods=['POST'])
@jwt_required()
def mpesa_payment():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user.id).first()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 77WdtapDOejakCeaxcVXuKDKlFTn'
    }

    payload = {
        "BusinessShortCode": 174379,
        "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjQwMzAxMDAxNzA1",
        "Timestamp": "20240301001705",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA":  int(user.phoneNumber),
        "PartyB": 174379,
        "PhoneNumber":  int(user.phoneNumber),
        "CallBackURL": "https://mydomain.com/path",
        "AccountReference": "CompanyXLTD",
        "TransactionDesc": "Payment of X"
    }

    try:
        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", headers=headers, json=payload)
        response.raise_for_status()
        return jsonify(response.json())

    except requests.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500


@transactions_bp.route('/cashTransfer/<string:phone_number>/<float:amount>', methods=['POST'])
@jwt_required()
def cash_transfer(phone_number, amount):
    current_user = get_jwt_identity()
    sender = current_user

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'}), 400

    try:
        if current_user.balance >= Decimal(amount):
            receiver = User.query.filter_by(phoneNumber=phone_number).first()

            if receiver:
                current_user.balance -= Decimal(amount)
                receiver.balance += Decimal(amount)

                new_transaction = Transaction(
                    sender=current_user, receiver=receiver, amount=Decimal(amount))
                db.session.add(new_transaction)
                db.session.commit()

                return jsonify({'message': 'Transaction successful'})

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'error': 'Transaction failed. Check user balance or recipient information.'}), 400


app.register_blueprint(transactions_bp)

if __name__ == '__main__':
    app.run(debug=True)
