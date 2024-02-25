from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, User, Transaction
import base64
import requests
from datetime import datetime

transactions_bp = Blueprint('transactions_bp', __name__)


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

            timestamp = generate_timestamp()
            key = "SJFuEzKXob9ztiXh1nGKZCsAFT2BDbQmPGNpQOp95GKw7ASM"
            secret = "AtQ9sa581NtvO8YB4E9m5VYsATlBLQSCAuG6ryr7slpApSgWe6ASrFuISxN1kxsg"

            token = authorization(
                "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
                key,
                secret
            )

            if token is not None:
                password = create_password(
                    "174379", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919", timestamp)

                payload = {
                    "BusinessShortCode": "174379",
                    "Password": password,
                    "Timestamp": timestamp,
                    "TransactionType": "CustomerPayBillOnline",
                    "Amount": str(amount),
                    "PartyA": sender.phoneNumber,  # Assuming sender has a phoneNumber attribute
                    "PartyB": "174379",
                    # Assuming receiver has a phoneNumber attribute
                    "PhoneNumber": receiver.phoneNumber,
                    "CallBackURL": "https://mydomain.com/pat",
                    "AccountReference": "Test",
                    "TransactionDesc": "Test"
                }

                headers = {"Authorization": "Bearer " + token}

                res = requests.post(
                    'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers=headers, json=payload
                )
                print(res.json())
            else:
                print("Failed to retrieve access token. Payment not processed.")

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
