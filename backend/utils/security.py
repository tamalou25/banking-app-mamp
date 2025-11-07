# backend/utils/security.py
import bcrypt
import re
import random
import string
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, get_jwt_identity

def hash_password(password):
    """Hash un mot de passe avec bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Vérifie un mot de passe contre son hash"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def validate_password_strength(password):
    """
    Valide la force d'un mot de passe
    Exigences: 8+ caractères, majuscule, minuscule, chiffre, caractère spécial
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial"
    
    return True, "Mot de passe valide"

def validate_email(email):
    """Valide le format d'une adresse email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_account_number():
    """Génère un numéro de compte bancaire unique à 11 chiffres"""
    return ''.join(random.choices(string.digits, k=11))

def generate_iban(country_code='FR', bank_code='12345678', branch_code='90000', account_number=None):
    """
    Génère un IBAN français valide
    Format: FR76 1234 5678 9000 XXXX XXXX XXX
    """
    if not account_number:
        account_number = generate_account_number()
    
    # Calcul de la clé de contrôle IBAN (simplifié)
    iban_base = f"{bank_code}{branch_code}{account_number}00"
    check_digits = 98 - (int(iban_base) % 97)
    
    iban = f"{country_code}{check_digits:02d}{bank_code}{branch_code}{account_number}"
    return iban

def validate_iban(iban):
    """Valide le format d'un IBAN"""
    iban = iban.replace(' ', '').upper()
    
    # Vérification longueur (France = 27 caractères)
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]+$', iban):
        return False
    
    if iban.startswith('FR') and len(iban) != 27:
        return False
    
    return True

def generate_reference_number():
    """Génère un numéro de référence unique pour les transactions"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TRX{timestamp}{random_part}"

def create_user_token(user_id, additional_claims=None):
    """Crée un token JWT pour un utilisateur"""
    identity = {'user_id': user_id}
    
    if additional_claims:
        identity.update(additional_claims)
    
    access_token = create_access_token(
        identity=identity,
        expires_delta=timedelta(hours=1)
    )
    
    return access_token

def sanitize_input(text):
    """Nettoie les entrées utilisateur pour prévenir les injections"""
    if not text:
        return text
    
    # Supprime les caractères dangereux
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()
