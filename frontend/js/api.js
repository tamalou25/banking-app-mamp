// frontend/js/api.js
const API_BASE_URL = 'http://localhost:5000/api';

// Stockage du token JWT
let authToken = localStorage.getItem('authToken');

// Fonction utilitaire pour les requêtes API
async function apiRequest(endpoint, options = {}) {
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    // Ajouter le token d'authentification si disponible
    if (authToken && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
        config.headers['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Une erreur est survenue');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentification
const AuthAPI = {
    async register(userData) {
        const data = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        if (data.token) {
            authToken = data.token;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('user', JSON.stringify(data));
        }
        
        return data;
    },

    async login(email, password) {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (data.token) {
            authToken = data.token;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('user', JSON.stringify(data.user));
        }
        
        return data;
    },

    async getProfile() {
        return await apiRequest('/auth/profile', {
            method: 'GET'
        });
    },

    logout() {
        authToken = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    },

    isAuthenticated() {
        return authToken !== null;
    }
};

// Gestion des comptes
const AccountsAPI = {
    async getAll() {
        return await apiRequest('/accounts/', {
            method: 'GET'
        });
    },

    async getById(accountId) {
        return await apiRequest(`/accounts/${accountId}`, {
            method: 'GET'
        });
    },

    async getSummary() {
        return await apiRequest('/accounts/summary', {
            method: 'GET'
        });
    }
};

// Gestion des transactions
const TransactionsAPI = {
    async getAll(page = 1, perPage = 10, accountId = null) {
        let endpoint = `/transactions/?page=${page}&per_page=${perPage}`;
        if (accountId) {
            endpoint += `&account_id=${accountId}`;
        }
        
        return await apiRequest(endpoint, {
            method: 'GET'
        });
    },

    async deposit(accountId, amount, description) {
        return await apiRequest('/transactions/deposit', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                amount: amount,
                description: description
            })
        });
    },

    async withdrawal(accountId, amount, description) {
        return await apiRequest('/transactions/withdrawal', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                amount: amount,
                description: description
            })
        });
    },

    async transfer(sourceAccountId, recipientIban, amount, description, recipientName) {
        return await apiRequest('/transactions/transfer', {
            method: 'POST',
            body: JSON.stringify({
                source_account_id: sourceAccountId,
                recipient_iban: recipientIban,
                amount: amount,
                description: description,
                recipient_name: recipientName
            })
        });
    },

    async payment(accountId, merchant, amount, category) {
        return await apiRequest('/transactions/payment', {
            method: 'POST',
            body: JSON.stringify({
                account_id: accountId,
                merchant: merchant,
                amount: amount,
                category: category
            })
        });
    }
};

// Vérifier l'authentification au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    const publicPages = ['login.html', 'register.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (!AuthAPI.isAuthenticated() && !publicPages.includes(currentPage)) {
        window.location.href = 'login.html';
    }
});
