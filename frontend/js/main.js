// frontend/js/main.js

let accounts = [];
let transactions = [];

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadUserProfile();
        await loadAccounts();
        await loadSummary();
        await loadTransactions();
        setupEventListeners();
    } catch (error) {
        showError('Erreur lors du chargement des données');
        console.error(error);
    }
});

// Charger le profil utilisateur
async function loadUserProfile() {
    try {
        const { user } = await AuthAPI.getProfile();
        document.getElementById('userName').textContent = `${user.first_name} ${user.last_name}`;
    } catch (error) {
        console.error('Erreur chargement profil:', error);
    }
}

// Charger les comptes
async function loadAccounts() {
    try {
        const data = await AccountsAPI.getAll();
        accounts = data.accounts;
        displayAccounts(accounts);
        populateAccountSelects(accounts);
    } catch (error) {
        console.error('Erreur chargement comptes:', error);
        showError('Impossible de charger les comptes');
    }
}

// Afficher les comptes
function displayAccounts(accounts) {
    const accountsList = document.getElementById('accountsList');
    accountsList.innerHTML = '';
    
    accounts.forEach(account => {
        const accountCard = document.createElement('div');
        accountCard.className = 'account-card';
        accountCard.innerHTML = `
            <div class="account-header">
                <h3>${getAccountTypeLabel(account.account_type)}</h3>
                <span class="account-number">${maskAccountNumber(account.account_number)}</span>
            </div>
            <div class="account-balance">
                <span class="balance-label">Solde</span>
                <span class="balance-value">${formatCurrency(account.balance)}</span>
            </div>
            <div class="account-footer">
                <span class="account-iban">${maskIBAN(account.iban)}</span>
            </div>
        `;
        accountsList.appendChild(accountCard);
    });
}

function getAccountTypeLabel(type) {
    const labels = {
        'courant': 'Compte Courant',
        'epargne': 'Compte Épargne',
        'joint': 'Compte Joint'
    };
    return labels[type] || type;
}

// Remplir les sélecteurs de compte
function populateAccountSelects(accounts) {
    const selects = [
        'depositAccount',
        'withdrawalAccount',
        'transferSourceAccount',
        'paymentAccount'
    ];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Sélectionnez un compte</option>';
        
        accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.id;
            option.textContent = `${getAccountTypeLabel(account.account_type)} - ${formatCurrency(account.balance)}`;
            select.appendChild(option);
        });
    });
}

// Charger le résumé
async function loadSummary() {
    try {
        const { summary } = await AccountsAPI.getSummary();
        document.getElementById('totalBalance').textContent = formatCurrency(summary.total_balance);
        document.getElementById('monthlyIncome').textContent = formatCurrency(summary.monthly_income || 0);
        document.getElementById('monthlyExpenses').textContent = formatCurrency(summary.monthly_expenses || 0);
    } catch (error) {
        console.error('Erreur chargement résumé:', error);
    }
}

// Charger les transactions
async function loadTransactions() {
    try {
        const data = await TransactionsAPI.getAll(1, 5);
        transactions = data.transactions;
        displayTransactions(transactions);
    } catch (error) {
        console.error('Erreur chargement transactions:', error);
    }
}

// Afficher les transactions
function displayTransactions(transactions) {
    const transactionsList = document.getElementById('transactionsList');
    transactionsList.innerHTML = '';
    
    if (transactions.length === 0) {
        transactionsList.innerHTML = '<p class="empty-state">Aucune transaction</p>';
        return;
    }
    
    transactions.forEach(transaction => {
        const transactionItem = document.createElement('div');
        transactionItem.className = 'transaction-item';
        
        const isPositive = ['deposit', 'transfer_in'].includes(transaction.transaction_type);
        const sign = isPositive ? '+' : '-';
        const colorClass = isPositive ? 'positive' : 'negative';
        
        transactionItem.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-type">${getTransactionLabel(transaction.transaction_type)}</div>
                <div class="transaction-description">${transaction.description || '-'}</div>
                <div class="transaction-date">${formatDate(transaction.transaction_date)}</div>
            </div>
            <div class="transaction-amount ${colorClass}">
                ${sign}${formatCurrency(transaction.amount)}
            </div>
        `;
        transactionsList.appendChild(transactionItem);
    });
}

// Configuration des écouteurs d'événements
function setupEventListeners() {
    // Déconnexion
    document.getElementById('logoutBtn').addEventListener('click', () => {
        if (confirm('Êtes-vous sûr de vouloir vous déconnecter ?')) {
            AuthAPI.logout();
        }
    });
    
    // Gestion des onglets
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            switchTab(tab);
        });
    });
    
    // Formulaires
    document.getElementById('depositForm').addEventListener('submit', handleDeposit);
    document.getElementById('withdrawalForm').addEventListener('submit', handleWithdrawal);
    document.getElementById('transferForm').addEventListener('submit', handleTransfer);
    document.getElementById('paymentForm').addEventListener('submit', handlePayment);
}

// Changer d'onglet
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tab) {
            btn.classList.add('active');
        }
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        if (content.dataset.content === tab) {
            content.classList.add('active');
        }
    });
}

// Gérer le dépôt
async function handleDeposit(e) {
    e.preventDefault();
    
    const accountId = parseInt(document.getElementById('depositAccount').value);
    const amount = parseFloat(document.getElementById('depositAmount').value);
    const description = document.getElementById('depositDescription').value;
    
    if (!accountId || !validateAmount(amount)) {
        showError('Veuillez remplir tous les champs correctement');
        return;
    }
    
    try {
        await TransactionsAPI.deposit(accountId, amount, description);
        showSuccess('Dépôt effectué avec succès !');
        document.getElementById('depositForm').reset();
        await refreshData();
    } catch (error) {
        showError(error.message || 'Erreur lors du dépôt');
    }
}

// Gérer le retrait
async function handleWithdrawal(e) {
    e.preventDefault();
    
    const accountId = parseInt(document.getElementById('withdrawalAccount').value);
    const amount = parseFloat(document.getElementById('withdrawalAmount').value);
    const description = document.getElementById('withdrawalDescription').value;
    
    if (!accountId || !validateAmount(amount)) {
        showError('Veuillez remplir tous les champs correctement');
        return;
    }
    
    try {
        await TransactionsAPI.withdrawal(accountId, amount, description);
        showSuccess('Retrait effectué avec succès !');
        document.getElementById('withdrawalForm').reset();
        await refreshData();
    } catch (error) {
        showError(error.message || 'Erreur lors du retrait');
    }
}

// Gérer le virement
async function handleTransfer(e) {
    e.preventDefault();
    
    const sourceAccountId = parseInt(document.getElementById('transferSourceAccount').value);
    const recipientIban = document.getElementById('transferRecipientIban').value;
    const recipientName = document.getElementById('transferRecipientName').value;
    const amount = parseFloat(document.getElementById('transferAmount').value);
    const description = document.getElementById('transferDescription').value;
    
    if (!sourceAccountId || !validateAmount(amount) || !validateIBAN(recipientIban)) {
        showError('Veuillez remplir tous les champs correctement');
        return;
    }
    
    try {
        await TransactionsAPI.transfer(sourceAccountId, recipientIban, amount, description, recipientName);
        showSuccess('Virement effectué avec succès !');
        document.getElementById('transferForm').reset();
        await refreshData();
    } catch (error) {
        showError(error.message || 'Erreur lors du virement');
    }
}

// Gérer le paiement
async function handlePayment(e) {
    e.preventDefault();
    
    const accountId = parseInt(document.getElementById('paymentAccount').value);
    const merchant = document.getElementById('paymentMerchant').value;
    const amount = parseFloat(document.getElementById('paymentAmount').value);
    const category = document.getElementById('paymentCategory').value;
    
    if (!accountId || !validateAmount(amount)) {
        showError('Veuillez remplir tous les champs correctement');
        return;
    }
    
    try {
        await TransactionsAPI.payment(accountId, merchant, amount, category);
        showSuccess('Paiement effectué avec succès !');
        document.getElementById('paymentForm').reset();
        await refreshData();
    } catch (error) {
        showError(error.message || 'Erreur lors du paiement');
    }
}

// Rafraîchir les données
async function refreshData() {
    await loadAccounts();
    await loadSummary();
    await loadTransactions();
}
