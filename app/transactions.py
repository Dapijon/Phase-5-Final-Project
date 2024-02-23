from models import db, Transaction
from flask import request, jsonify
from datetime import datetime
from flask import request, redirect, flash, jsonify
from user_bp import login_required, current_user
from models import db, User, Transaction
import locale
import requests


@app.route('/cash_transfer/<int:receiver_id>/<float:amount>', methods=['POST'])
@login_required
def cash_transfer(receiver_id, amount):
    sender = current_user.id

    if current_user.balance >= amount:
        try:
            current_user.balance -= amount
            receiver = User.query.get(receiver_id)
            receiver.balance += amount

            new_transaction = Transaction(
                sender=current_user, receiver=receiver, amount=amount)
            db.session.add(new_transaction)

            db.session.commit()

            return jsonify({'message': 'Transaction successful'})
        except Exception as e:
            return jsonify({'error': f"Error: {str(e)}"})
    else:
        return jsonify({'error': 'Insufficient funds'})


@app.route('/deposit', methods=['POST'])
@login_required
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


@app.route('/withdraw', methods=['POST'])
@login_required
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
