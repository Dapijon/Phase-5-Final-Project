from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, User, Transaction

summary_bp = Blueprint( 'summary_bp', __name__)

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


