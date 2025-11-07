# backend/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.database import execute_query
from utils.security import (
    hash_password, 
    verify_password, 
    validate_password_strength,
    validate_email,
    create_user_token,
    generate_account_number,
    generate_iban,
    sanitize_input
)
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Validation de l'email
        if not validate_email(data['email']):
            return jsonify({'error': 'Format d\'email invalide'}), 400
        
        # Validation de la force du mot de passe
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Nettoyage des entrées
        email = sanitize_input(data['email'].lower())
        username = sanitize_input(data['username'].lower())
        first_name = sanitize_input(data['first_name'])
        last_name = sanitize_input(data['last_name'])
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = execute_query(
            "SELECT id FROM users WHERE email = %s OR username = %s",
            (email, username)
        )
        
        if existing_user:
            return jsonify({'error': 'Cet email ou nom d\'utilisateur existe déjà'}), 409
        
        # Hacher le mot de passe
        password_hash = hash_password(data['password'])
        
        # Insérer l'utilisateur dans la base de données
        user_id = execute_query(
            """
            INSERT INTO users (email, username, password_hash, first_name, last_name, 
                             phone_number, date_of_birth, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                email,
                username,
                password_hash,
                first_name,
                last_name,
                data.get('phone_number'),
                data.get('date_of_birth'),
                data.get('address')
            ),
            commit=True
        )
        
        # Créer automatiquement un compte courant pour le nouvel utilisateur
        account_number = generate_account_number()
        iban = generate_iban(account_number=account_number)
        
        execute_query(
            """
            INSERT INTO accounts (user_id, account_number, account_type, balance, 
                                iban, overdraft_limit)
            VALUES (%s, %s, 'courant', 0.00, %s, 500.00)
            """,
            (user_id, account_number, iban),
            commit=True
        )
        
        # Créer un token JWT
        token = create_user_token(user_id, {'username': username})
        
        return jsonify({
            'message': 'Inscription réussie',
            'user_id': user_id,
            'token': token,
            'username': username
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'inscription: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des champs requis
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        email = sanitize_input(data['email'].lower())
        
        # Rechercher l'utilisateur
        user = execute_query(
            """
            SELECT id, email, username, password_hash, first_name, last_name, is_active
            FROM users WHERE email = %s
            """,
            (email,)
        )
        
        if not user:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        user = user[0]
        
        # Vérifier si le compte est actif
        if not user['is_active']:
            return jsonify({'error': 'Compte désactivé'}), 403
        
        # Vérifier le mot de passe
        if not verify_password(data['password'], user['password_hash']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Mettre à jour la date de dernière connexion
        execute_query(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.now(), user['id']),
            commit=True
        )
        
        # Créer un token JWT
        token = create_user_token(user['id'], {'username': user['username']})
        
        return jsonify({
            'message': 'Connexion réussie',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la connexion: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Récupère le profil de l'utilisateur connecté"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        
        user = execute_query(
            """
            SELECT id, email, username, first_name, last_name, phone_number,
                   date_of_birth, address, created_at, last_login
            FROM users WHERE id = %s
            """,
            (user_id,)
        )
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        user_data = user[0]
        
        # Convertir les dates en chaînes ISO
        for field in ['created_at', 'last_login', 'date_of_birth']:
            if user_data.get(field):
                user_data[field] = user_data[field].isoformat()
        
        return jsonify({'user': user_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération du profil: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change le mot de passe de l'utilisateur"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Mot de passe actuel et nouveau requis'}), 400
        
        # Récupérer le hash actuel
        user = execute_query(
            "SELECT password_hash FROM users WHERE id = %s",
            (user_id,)
        )
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Vérifier le mot de passe actuel
        if not verify_password(data['current_password'], user[0]['password_hash']):
            return jsonify({'error': 'Mot de passe actuel incorrect'}), 401
        
        # Valider le nouveau mot de passe
        is_valid, message = validate_password_strength(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Hacher le nouveau mot de passe
        new_password_hash = hash_password(data['new_password'])
        
        # Mettre à jour le mot de passe
        execute_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, user_id),
            commit=True
        )
        
        return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du changement de mot de passe: {str(e)}'}), 500
