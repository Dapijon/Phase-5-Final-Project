from datetime import datetime
import requests
import base64
from .models import db, User, Transaction
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, request
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError
User


transactions_bp = Blueprint('transactions_bp', __name__)


@transactions_bp.route('/makeDeposit', methods=['POST'])
@jwt_required()
def make_deposit():
    current_user = get_jwt_identity()
    amount = request.json.get('amount')

    try:
        if amount > 0:
            current_user.balance += Decimal(amount)

            new_transaction = Transaction(
                sender=current_user, receiver=current_user, amount=Decimal(amount))
            db.session.add(new_transaction)
            db.session.commit()

            return jsonify({'message': 'Deposit successful'})
        else:
            return jsonify({'error': 'Amount must be greater than zero'})
    except SQLAlchemyError as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f"Error: {str(e)}"})


def authorization(url, key, secret):
    plain_text = f'{key}:{secret}'
    bytes_obj = bytes(plain_text, 'utf-8')
    bs4 = base64.b64encode(bytes_obj)

    headers = {"Authorization": "Basic " + bs4.decode('utf-8')}

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json().get('access_token')
    except requests.RequestException as e:
        print(f"Error during access token retrieval: {e}")
        print(f"Response content: {res.text}")
        return None


def generate_timestamp():
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


def create_password(shortcode, passkey, timestamp):
    plain_text = f"{shortcode}{passkey}{timestamp}"
    bytes_obj = bytes(plain_text, 'utf-8')
    bs4 = base64.b64encode(bytes_obj)
    generated_password = bs4.decode('utf-8')
    print(f"Generated Password: {generated_password}")
    return generated_password


@transactions_bp.route('/cashTransfer/<string:phone_number>/<float:amount>', methods=['POST'])
@jwt_required()
def cash_transfer(phone_number, amount):
    current_user = get_jwt_identity()
    sender = current_user

    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'})

    try:
        if current_user.balance >= Decimal(amount):

            receiver = User.query.filter_by(phoneNumber=phone_number).first()

            if receiver:
                current_user.balance -= Decimal(amount)
                receiver.balance += Decimal(amount)

                timestamp = generate_timestamp()
                key = "SJFuEzKXob9ztiXh1nGKZCsAFT2BDbQmPGNpQOp95GKw7ASM"
                secret = "AtQ9sa581NtvO8YB4E9m5VYsATlBLQSCAuG6ryr7slpApSgWe6ASrFuISxN1kxsg"

                token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
                payment_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

                token = authorization(token_url, key, secret)

                if token is not None:
                    password = create_password(
                        "174379", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919", timestamp)

                    payload = {
                        "BusinessShortCode": "174379",
                        "Password": password,
                        "Timestamp": timestamp,
                        "TransactionType": "CustomerPayBillOnline",
                        "Amount": str(amount),
                        "PartyA": sender.phoneNumber,
                        "PartyB": "174379",
                        "PhoneNumber": receiver.phoneNumber,
                        "CallBackURL": "https://mydomain.com/pat",
                        "AccountReference": "Test",
                        "TransactionDesc": "Test"
                    }

                    headers = {"Authorization": "Bearer " + token}

                    try:
                        res = requests.post(
                            payment_url, headers=headers, json=payload)
                        res.raise_for_status()
                        print(res.json())
                    except requests.RequestException as e:
                        print(f"Error during MPESA transaction: {e}")
                        print(f"Response content: {res.text}")
                        return jsonify({'error': 'Failed to process MPESA transaction'})

                    new_transaction = Transaction(
                        sender=current_user, receiver=receiver, amount=Decimal(amount))
                    db.session.add(new_transaction)
                    db.session.commit()

                    return jsonify({'message': 'Transaction successful'})
                else:
                    print("Failed to retrieve access token. Payment not processed.")
                    return jsonify({'error': 'Failed to retrieve access token'})
            else:
                return jsonify({'error': 'Receiver not found'})
        else:
            return jsonify({'error': 'Insufficient funds'})
    except SQLAlchemyError as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f"Error: {str(e)}"})
