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
def get_user_summary():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if user is None:
            return jsonify({'error': 'User not found'}), 404

        send_transactions = Transaction.query.filter_by(sender_id=current_user_id).all()
        send_amount = sum(transaction.amount for transaction in send_transactions)
        
        received_transactions = Transaction.query.filter_by(receiver_id=current_user_id).all()
        received_amount = sum(transaction.amount for transaction in received_transactions)

        summary_data = {
            'send_transactions': len(send_transactions),
            'send_amount': send_amount,
            'received_transactions': len(received_transactions),
            'received_amount': received_amount,
            'total_balance': user.balance
        }
        
        return jsonify(summary_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
@login_required
@admin_required
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
        'is_admin': user.is_admin,
        'created_at': user.created_at,
        'updated_at': user.updated_at,
    } for user in users]
    return jsonify(users_data), 200


@summary_bp.route('/user-transactions/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_transactions(user_id):
    try:
       
        current_user_id = get_jwt_identity()
        if current_user_id != user_id:
            return jsonify({'error': 'Unauthorized access to user transactions'}), 403

       
        user = User.query.get(user_id)
        if user is None:
            return jsonify({'error': 'User not found'}), 404

       
        transactions = Transaction.query.filter(
            (Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)
        ).all()

        
        serialized_transactions = [{
            'id': transaction.id,
            'sender_id': transaction.sender_id,
            'receiver_id': transaction.receiver_id,
            'amount': transaction.amount,
           
        } for transaction in transactions]

        return jsonify(serialized_transactions), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'An unexpected error occurred'}), 500



@summary_bp.route('/transactions/summary')
@login_required
@admin_required
def transactions_summary():
   
    transactions = Transaction.query.all()
    total_transactions = len(transactions)
    total_amount = sum(transaction.amount for transaction in transactions)
    return jsonify({
        'total_transactions': total_transactions,
        'total_amount': total_amount
    }), 200


@summary_bp.route('/analytics')
@admin_required
@login_required
def analytics():
   
    total_amount_sent = db.session.query(
        db.func.sum(Transaction.amount)).scalar() or 0

   
    total_balance = db.session.query(db.func.sum(User.balance)).scalar() or 0

    return jsonify({
        'total_amount_sent': total_amount_sent,
        'total_balance': total_balance
    }), 200


@summary_bp.route('/make-admin/<int:user_id>', methods=['PUT'])
@admin_required
def make_admin(user_id):

    user = User.query.get(user_id)
    if user:
        user.is_admin = True
        db.session.commit()
        return jsonify({'message': 'User has been made admin'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@summary_bp.route('/remove-admin/<int:user_id>', methods=['PUT'])
@admin_required
def remove_admin(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_admin = False
        db.session.commit()
        return jsonify({'message': 'Admin status removed successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@summary_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
  
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User has been deleted successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404



