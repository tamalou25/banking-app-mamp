// frontend/js/utils.js

// Formater un montant en devise
function formatCurrency(amount, currency = 'EUR') {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// Formater une date
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Formater une date courte
function formatShortDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(date);
}

// Masquer un numéro de compte
function maskAccountNumber(accountNumber) {
    if (!accountNumber || accountNumber.length < 4) return accountNumber;
    return '**** **** ' + accountNumber.slice(-4);
}

// Masquer un IBAN
function maskIBAN(iban) {
    if (!iban || iban.length < 4) return iban;
    return iban.substring(0, 4) + ' **** **** **** ' + iban.slice(-4);
}

// Obtenir la couleur selon le type de transaction
function getTransactionColor(type) {
    const colors = {
        'deposit': 'var(--color-success)',
        'transfer_in': 'var(--color-success)',
        'withdrawal': 'var(--color-error)',
        'transfer_out': 'var(--color-error)',
        'payment': 'var(--color-error)',
        'interest': 'var(--color-info)',
        'fee': 'var(--color-warning)'
    };
    return colors[type] || 'var(--color-text)';
}

// Obtenir le libellé d'un type de transaction
function getTransactionLabel(type) {
    const labels = {
        'deposit': 'Dépôt',
        'withdrawal': 'Retrait',
        'transfer_out': 'Virement envoyé',
        'transfer_in': 'Virement reçu',
        'payment': 'Paiement',
        'interest': 'Intérêts',
        'fee': 'Frais'
    };
    return labels[type] || type;
}

// Obtenir le libellé d'une catégorie
function getCategoryLabel(category) {
    const labels = {
        'alimentation': 'Alimentation',
        'logement': 'Logement',
        'transport': 'Transport',
        'loisirs': 'Loisirs',
        'sante': 'Santé',
        'shopping': 'Shopping',
        'services': 'Services',
        'salary': 'Salaire',
        'refund': 'Remboursement',
        'autres': 'Autres'
    };
    return labels[category] || category;
}

// Afficher un message de succès
function showSuccess(message) {
    showNotification(message, 'success');
}

// Afficher un message d'erreur
function showError(message) {
    showNotification(message, 'error');
}

// Afficher une notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: var(--color-surface);
        border-left: 4px solid var(--color-${type === 'error' ? 'error' : type === 'success' ? 'success' : 'info'});
        border-radius: var(--radius-base);
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
        color: var(--color-text);
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Valider un email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Valider un IBAN
function validateIBAN(iban) {
    const cleanIban = iban.replace(/\s/g, '');
    return /^[A-Z]{2}\d{2}[A-Z0-9]+$/.test(cleanIban) && cleanIban.length >= 15;
}

// Valider un montant
function validateAmount(amount) {
    const num = parseFloat(amount);
    return !isNaN(num) && num > 0;
}

// Ajouter les styles pour les animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
