from functools import wraps
from flask import Blueprint, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_login import login_required, current_user
from .models import db, User, Transaction

summary_bp = Blueprint( 'summary_bp', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # HTTP 403 Forbidden error
        return f(*args, **kwargs)
    return decorated_function


@summary_bp.route('/user-summary')
@jwt_required()
def get_userSummary():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    send_transactions = Transaction.query.filter_by(sender_id=current_user_id).all()
    received_transactions = Transaction.query.filter_by(receiver_id=current_user_id).all()
    
    send_amount = sum(transaction.amount for transaction in send_transactions)
    received_amount = sum(transaction.amount for transaction in received_transactions)
    
    summary_data = {
        'send_transactions': len(send_transactions),
        'send_amount': send_amount,
        'received_transactions': len(received_transactions),
        'received_amount': received_amount,
        'total_balance': user.balance
    }
    
    return jsonify(summary_data), 200

@summary_bp.route('/transaction_summary', methods=['GET'])
@jwt_required()
def admin_transaction_summary():
    transactions = Transaction.query.all()
    
    send_transactions = sum(transaction.amount for transaction in transactions if transaction.sender_id)
    received_transactions = sum(transaction.amount for transaction in transactions if transaction.receiver_id)
    
    summary_data = {
        'total_send_transactions': len(send_transactions),
        'total_send_amount': send_transactions,
        'total_received_transactions': len(received_transactions),
        'total_received_amount': received_transactions
    }
    
    return jsonify(summary_data), 200





@summary_bp.route('/users')
# @login_required
# @admin_required
def get_users():
    if not current_user.is_admin:
        return jsonify({'message': 'Unauthorized access'}), 403
    users = User.query.all()
    users_data = [{
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'national_ID': user.national_ID,
        'phoneNumber': user.phoneNumber,
        'balance': user.balance,
    } for user in users]
    return jsonify(users_data), 200


@summary_bp.route('/transactions/summary')
@login_required
@admin_required
def transactions_summary():
    # Logic to retrieve transaction summary
    transactions = Transaction.query.all()
    total_transactions = len(transactions)
    total_amount = sum(transaction.amount for transaction in transactions)
    return jsonify({
        'total_transactions': total_transactions,
        'total_amount': total_amount
    }), 200


@summary_bp.route('/analytics')
@admin_required
def analytics():
    # Calculate sum of amount sent
    total_amount_sent = db.session.query(
        db.func.sum(Transaction.amount)).scalar() or 0

    # Calculate total balance of all users
    total_balance = db.session.query(db.func.sum(User.balance)).scalar() or 0

    return jsonify({
        'total_amount_sent': total_amount_sent,
        'total_balance': total_balance
    }), 200


@summary_bp.route('/make-admin/<int:user_id>', methods=['PUT'])
@admin_required
def make_admin(user_id):
    # Find the user by user_id
    user = User.query.get(user_id)
    if user:
        user.is_admin = True
        db.session.commit()
        return jsonify({'message': 'User has been made admin'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404



