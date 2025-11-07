# backend/utils/validators.py
import re
from decimal import Decimal

def validate_amount(amount):
    """Valide un montant financier"""
    try:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            return False, "Le montant doit être positif"
        if amount_decimal > Decimal('1000000'):
            return False, "Le montant dépasse la limite autorisée"
        return True, "Montant valide"
    except:
        return False, "Format de montant invalide"

def validate_account_type(account_type):
    """Valide le type de compte"""
    valid_types = ['courant', 'epargne', 'joint']
    return account_type in valid_types

def validate_transaction_category(category):
    """Valide la catégorie de transaction"""
    valid_categories = [
        'alimentation', 'logement', 'transport', 'loisirs',
        'santé', 'shopping', 'services', 'salary', 'refund', 'autres'
    ]
    return category in valid_categories
