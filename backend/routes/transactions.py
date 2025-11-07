# backend/routes/transactions.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.database import execute_query, get_db_connection
from utils.security import validate_iban, generate_reference_number, sanitize_input
from decimal import Decimal
from datetime import datetime
import mysql.connector

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    """Récupère l'historique des transactions de l'utilisateur"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        
        # Paramètres de pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        account_id = request.args.get('account_id', type=int)
        
        offset = (page - 1) * per_page
        
        # Construire la requête avec filtres
        query = """
            SELECT t.id, t.transaction_type, t.amount, t.balance_after, 
                   t.description, t.recipient_name, t.category, t.status, 
                   t.transaction_date, t.reference_number,
                   a.account_number, a.account_type
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = %s
        """
        
        params = [user_id]
        
        if account_id:
            query += " AND t.account_id = %s"
            params.append(account_id)
        
        query += " ORDER BY t.transaction_date DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        transactions = execute_query(query, tuple(params))
        
        # Formater les résultats
        for transaction in transactions:
            transaction['amount'] = float(transaction['amount'])
            transaction['balance_after'] = float(transaction['balance_after'])
            if transaction.get('transaction_date'):
                transaction['transaction_date'] = transaction['transaction_date'].isoformat()
        
        # Compter le total pour la pagination
        count_query = """
            SELECT COUNT(*) as total
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = %s
        """
        count_params = [user_id]
        
        if account_id:
            count_query += " AND t.account_id = %s"
            count_params.append(account_id)
        
        total = execute_query(count_query, tuple(count_params))[0]['total']
        
        return jsonify({
            'transactions': transactions,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des transactions: {str(e)}'}), 500

@transactions_bp.route('/deposit', methods=['POST'])
@jwt_required()
def create_deposit():
    """Effectue un dépôt sur un compte"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        data = request.get_json()
        
        # Validation
        if not data.get('account_id') or not data.get('amount'):
            return jsonify({'error': 'ID du compte et montant requis'}), 400
        
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            return jsonify({'error': 'Le montant doit être positif'}), 400
        
        account_id = data['account_id']
        description = sanitize_input(data.get('description', 'Dépôt'))
        
        # Vérifier que le compte appartient à l'utilisateur
        account = execute_query(
            "SELECT id, balance FROM accounts WHERE id = %s AND user_id = %s AND status = 'active'",
            (account_id, user_id)
        )
        
        if not account:
            return jsonify({'error': 'Compte non trouvé ou inactif'}), 404
        
        current_balance = account[0]['balance']
        new_balance = current_balance + amount
        
        # Transaction atomique
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            # Mettre à jour le solde du compte
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, account_id)
            )
            
            # Créer la transaction
            reference = generate_reference_number()
            cursor.execute(
                """
                INSERT INTO transactions (account_id, transaction_type, amount, balance_after, 
                                        description, status, reference_number)
                VALUES (%s, 'deposit', %s, %s, %s, 'completed', %s)
                """,
                (account_id, amount, new_balance, description, reference)
            )
            
            connection.commit()
            transaction_id = cursor.lastrowid
            
            return jsonify({
                'message': 'Dépôt effectué avec succès',
                'transaction_id': transaction_id,
                'reference': reference,
                'new_balance': float(new_balance)
            }), 201
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du dépôt: {str(e)}'}), 500

@transactions_bp.route('/withdrawal', methods=['POST'])
@jwt_required()
def create_withdrawal():
    """Effectue un retrait sur un compte"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        data = request.get_json()
        
        if not data.get('account_id') or not data.get('amount'):
            return jsonify({'error': 'ID du compte et montant requis'}), 400
        
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            return jsonify({'error': 'Le montant doit être positif'}), 400
        
        account_id = data['account_id']
        description = sanitize_input(data.get('description', 'Retrait'))
        
        account = execute_query(
            "SELECT id, balance, overdraft_limit FROM accounts WHERE id = %s AND user_id = %s AND status = 'active'",
            (account_id, user_id)
        )
        
        if not account:
            return jsonify({'error': 'Compte non trouvé ou inactif'}), 404
        
        current_balance = account[0]['balance']
        overdraft_limit = account[0]['overdraft_limit']
        available_balance = current_balance + overdraft_limit
        
        if amount > available_balance:
            return jsonify({
                'error': 'Solde insuffisant',
                'current_balance': float(current_balance),
                'requested_amount': float(amount),
                'available': float(available_balance)
            }), 400
        
        new_balance = current_balance - amount
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, account_id)
            )
            
            reference = generate_reference_number()
            cursor.execute(
                """
                INSERT INTO transactions (account_id, transaction_type, amount, balance_after, 
                                        description, status, reference_number)
                VALUES (%s, 'withdrawal', %s, %s, %s, 'completed', %s)
                """,
                (account_id, amount, new_balance, description, reference)
            )
            
            connection.commit()
            transaction_id = cursor.lastrowid
            
            return jsonify({
                'message': 'Retrait effectué avec succès',
                'transaction_id': transaction_id,
                'reference': reference,
                'new_balance': float(new_balance)
            }), 201
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du retrait: {str(e)}'}), 500

@transactions_bp.route('/transfer', methods=['POST'])
@jwt_required()
def create_transfer():
    """Effectue un virement entre comptes"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        data = request.get_json()
        
        required_fields = ['source_account_id', 'recipient_iban', 'amount', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            return jsonify({'error': 'Le montant doit être positif'}), 400
        
        recipient_iban = data['recipient_iban'].replace(' ', '')
        if not validate_iban(recipient_iban):
            return jsonify({'error': 'IBAN invalide'}), 400
        
        source_account_id = data['source_account_id']
        description = sanitize_input(data['description'])
        recipient_name = sanitize_input(data.get('recipient_name', 'Bénéficiaire'))
        
        source_account = execute_query(
            "SELECT id, balance, overdraft_limit FROM accounts WHERE id = %s AND user_id = %s AND status = 'active'",
            (source_account_id, user_id)
        )
        
        if not source_account:
            return jsonify({'error': 'Compte source non trouvé'}), 404
        
        current_balance = source_account[0]['balance']
        overdraft_limit = source_account[0]['overdraft_limit']
        available_balance = current_balance + overdraft_limit
        
        if amount > available_balance:
            return jsonify({'error': 'Solde insuffisant'}), 400
        
        new_source_balance = current_balance - amount
        
        recipient_account = execute_query(
            "SELECT id, balance FROM accounts WHERE iban = %s AND status = 'active'",
            (recipient_iban,)
        )
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            reference = generate_reference_number()
            
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_source_balance, source_account_id)
            )
            
            cursor.execute(
                """
                INSERT INTO transactions (account_id, transaction_type, amount, balance_after, 
                                        description, recipient_iban, recipient_name, status, reference_number)
                VALUES (%s, 'transfer_out', %s, %s, %s, %s, %s, 'completed', %s)
                """,
                (source_account_id, amount, new_source_balance, description, recipient_iban, recipient_name, reference)
            )
            
            if recipient_account:
                recipient_id = recipient_account[0]['id']
                recipient_balance = recipient_account[0]['balance']
                new_recipient_balance = recipient_balance + amount
                
                cursor.execute(
                    "UPDATE accounts SET balance = %s WHERE id = %s",
                    (new_recipient_balance, recipient_id)
                )
                
                cursor.execute(
                    """
                    INSERT INTO transactions (account_id, transaction_type, amount, balance_after, 
                                            description, status, reference_number)
                    VALUES (%s, 'transfer_in', %s, %s, %s, 'completed', %s)
                    """,
                    (recipient_id, amount, new_recipient_balance, f"Virement reçu - {description}", reference)
                )
            
            connection.commit()
            
            return jsonify({
                'message': 'Virement effectué avec succès',
                'reference': reference,
                'new_balance': float(new_source_balance),
                'amount_transferred': float(amount)
            }), 201
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du virement: {str(e)}'}), 500

@transactions_bp.route('/payment', methods=['POST'])
@jwt_required()
def create_payment():
    """Effectue un paiement (achat)"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        data = request.get_json()
        
        required_fields = ['account_id', 'merchant', 'amount', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            return jsonify({'error': 'Le montant doit être positif'}), 400
        
        account_id = data['account_id']
        merchant = sanitize_input(data['merchant'])
        category = sanitize_input(data['category'])
        
        account = execute_query(
            "SELECT id, balance, overdraft_limit FROM accounts WHERE id = %s AND user_id = %s AND status = 'active'",
            (account_id, user_id)
        )
        
        if not account:
            return jsonify({'error': 'Compte non trouvé'}), 404
        
        current_balance = account[0]['balance']
        overdraft_limit = account[0]['overdraft_limit']
        available_balance = current_balance + overdraft_limit
        
        if amount > available_balance:
            return jsonify({'error': 'Solde insuffisant'}), 400
        
        new_balance = current_balance - amount
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, account_id)
            )
            
            reference = generate_reference_number()
            cursor.execute(
                """
                INSERT INTO transactions (account_id, transaction_type, amount, balance_after, 
                                        description, category, status, reference_number)
                VALUES (%s, 'payment', %s, %s, %s, %s, 'completed', %s)
                """,
                (account_id, amount, new_balance, merchant, category, reference)
            )
            
            connection.commit()
            transaction_id = cursor.lastrowid
            
            return jsonify({
                'message': 'Paiement effectué avec succès',
                'transaction_id': transaction_id,
                'reference': reference,
                'new_balance': float(new_balance)
            }), 201
            
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du paiement: {str(e)}'}), 500
