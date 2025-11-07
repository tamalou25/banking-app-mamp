# backend/routes/accounts.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.database import execute_query
from decimal import Decimal

accounts_bp = Blueprint('accounts', __name__)

def decimal_to_float(obj):
    """Convertit les Decimal en float pour la sérialisation JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

@accounts_bp.route('/', methods=['GET'])
@jwt_required()
def get_accounts():
    """Récupère tous les comptes de l'utilisateur"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        
        accounts = execute_query(
            """
            SELECT id, account_number, account_type, balance, currency, iban, 
                   status, overdraft_limit, interest_rate, created_at
            FROM accounts
            WHERE user_id = %s AND status != 'closed'
            ORDER BY created_at ASC
            """,
            (user_id,)
        )
        
        # Convertir les Decimal en float et les dates en ISO
        for account in accounts:
            account['balance'] = float(account['balance'])
            account['overdraft_limit'] = float(account['overdraft_limit'])
            account['interest_rate'] = float(account['interest_rate'])
            if account.get('created_at'):
                account['created_at'] = account['created_at'].isoformat()
        
        return jsonify({'accounts': accounts}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des comptes: {str(e)}'}), 500

@accounts_bp.route('/<int:account_id>', methods=['GET'])
@jwt_required()
def get_account_details(account_id):
    """Récupère les détails d'un compte spécifique"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        
        account = execute_query(
            """
            SELECT a.id, a.account_number, a.account_type, a.balance, a.currency, 
                   a.iban, a.status, a.overdraft_limit, a.interest_rate, a.created_at,
                   u.first_name, u.last_name
            FROM accounts a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = %s AND a.user_id = %s
            """,
            (account_id, user_id)
        )
        
        if not account:
            return jsonify({'error': 'Compte non trouvé'}), 404
        
        account_data = account[0]
        account_data['balance'] = float(account_data['balance'])
        account_data['overdraft_limit'] = float(account_data['overdraft_limit'])
        account_data['interest_rate'] = float(account_data['interest_rate'])
        
        if account_data.get('created_at'):
            account_data['created_at'] = account_data['created_at'].isoformat()
        
        return jsonify({'account': account_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération du compte: {str(e)}'}), 500

@accounts_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_accounts_summary():
    """Récupère un résumé de tous les comptes (solde total, etc.)"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        
        # Récupérer le solde total
        result = execute_query(
            """
            SELECT 
                COUNT(*) as total_accounts,
                COALESCE(SUM(balance), 0) as total_balance,
                COALESCE(SUM(CASE WHEN account_type = 'courant' THEN balance ELSE 0 END), 0) as checking_balance,
                COALESCE(SUM(CASE WHEN account_type = 'epargne' THEN balance ELSE 0 END), 0) as savings_balance
            FROM accounts
            WHERE user_id = %s AND status = 'active'
            """,
            (user_id,)
        )
        
        summary = result[0]
        summary['total_balance'] = float(summary['total_balance'] or 0)
        summary['checking_balance'] = float(summary['checking_balance'] or 0)
        summary['savings_balance'] = float(summary['savings_balance'] or 0)
        
        # Récupérer les statistiques mensuelles
        monthly_stats = execute_query(
            """
            SELECT 
                COALESCE(SUM(CASE WHEN t.transaction_type IN ('deposit', 'transfer_in') THEN t.amount ELSE 0 END), 0) as monthly_income,
                COALESCE(SUM(CASE WHEN t.transaction_type IN ('withdrawal', 'transfer_out', 'payment') THEN t.amount ELSE 0 END), 0) as monthly_expenses
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = %s 
            AND t.transaction_date >= DATE_FORMAT(NOW(), '%%Y-%%m-01')
            AND t.status = 'completed'
            """,
            (user_id,)
        )
        
        if monthly_stats:
            summary['monthly_income'] = float(monthly_stats[0]['monthly_income'] or 0)
            summary['monthly_expenses'] = float(monthly_stats[0]['monthly_expenses'] or 0)
            summary['monthly_savings'] = summary['monthly_income'] - summary['monthly_expenses']
        
        return jsonify({'summary': summary}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération du résumé: {str(e)}'}), 500
