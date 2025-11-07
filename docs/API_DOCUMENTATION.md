# Documentation API - Banque Digital

## Base URL

```
http://localhost:5000/api
```

## Authentification

L'API utilise des tokens JWT (JSON Web Token) pour l'authentification. Le token doit être inclus dans l'en-tête de chaque requête authentifiée :

```
Authorization: Bearer <votre_token_jwt>
```

## Endpoints

### Authentification

#### POST /auth/register
Crée un nouvel utilisateur.

**Corps de la requête :**
```json
{
  "email": "user@example.com",
  "username": "utilisateur",
  "password": "MotDePasse123!",
  "first_name": "Prénom",
  "last_name": "Nom",
  "phone_number": "+33612345678",
  "date_of_birth": "1990-01-01",
  "address": "123 Rue Example, Paris"
}
```

**Réponse (201) :**
```json
{
  "message": "Inscription réussie",
  "user_id": 1,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "username": "utilisateur"
}
```

#### POST /auth/login
Connecte un utilisateur existant.

**Corps de la requête :**
```json
{
  "email": "user@example.com",
  "password": "MotDePasse123!"
}
```

**Réponse (200) :**
```json
{
  "message": "Connexion réussie",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "utilisateur",
    "email": "user@example.com",
    "first_name": "Prénom",
    "last_name": "Nom"
  }
}
```

#### GET /auth/profile
Récupère le profil de l'utilisateur connecté.

**En-têtes requis :**
```
Authorization: Bearer <token>
```

**Réponse (200) :**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "utilisateur",
    "first_name": "Prénom",
    "last_name": "Nom",
    "phone_number": "+33612345678",
    "date_of_birth": "1990-01-01",
    "address": "123 Rue Example, Paris",
    "created_at": "2024-01-01T10:00:00",
    "last_login": "2024-01-15T14:30:00"
  }
}
```

### Comptes

#### GET /accounts/
Récupère tous les comptes de l'utilisateur.

**Réponse (200) :**
```json
{
  "accounts": [
    {
      "id": 1,
      "account_number": "00000000001",
      "account_type": "courant",
      "balance": 12547.50,
      "currency": "EUR",
      "iban": "FR7612345678900000000001234",
      "status": "active",
      "overdraft_limit": 500.00,
      "interest_rate": 0.0000,
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

#### GET /accounts/{account_id}
Récupère les détails d'un compte spécifique.

**Réponse (200) :**
```json
{
  "account": {
    "id": 1,
    "account_number": "00000000001",
    "account_type": "courant",
    "balance": 12547.50,
    "currency": "EUR",
    "iban": "FR7612345678900000000001234",
    "status": "active",
    "overdraft_limit": 500.00,
    "interest_rate": 0.0000,
    "created_at": "2024-01-01T10:00:00",
    "first_name": "Prénom",
    "last_name": "Nom"
  }
}
```

#### GET /accounts/summary
Récupère un résumé financier de tous les comptes.

**Réponse (200) :**
```json
{
  "summary": {
    "total_accounts": 2,
    "total_balance": 15847.50,
    "checking_balance": 12547.50,
    "savings_balance": 3300.00,
    "monthly_income": 3285.00,
    "monthly_expenses": 1090.94,
    "monthly_savings": 2194.06
  }
}
```

### Transactions

#### GET /transactions/
Récupère l'historique des transactions.

**Paramètres de requête :**
- `page` (optionnel): Numéro de page (défaut: 1)
- `per_page` (optionnel): Résultats par page (défaut: 10, max: 100)
- `account_id` (optionnel): Filtrer par ID de compte

**Réponse (200) :**
```json
{
  "transactions": [
    {
      "id": 1,
      "transaction_type": "deposit",
      "amount": 3200.00,
      "balance_after": 12547.50,
      "description": "Salaire - Entreprise ABC",
      "recipient_name": null,
      "category": "salary",
      "status": "completed",
      "transaction_date": "2024-01-15T10:00:00",
      "reference_number": "TRX001",
      "account_number": "00000000001",
      "account_type": "courant"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 5,
    "pages": 1
  }
}
```

#### POST /transactions/deposit
Effectue un dépôt sur un compte.

**Corps de la requête :**
```json
{
  "account_id": 1,
  "amount": 500.00,
  "description": "Dépôt en espèces"
}
```

**Réponse (201) :**
```json
{
  "message": "Dépôt effectué avec succès",
  "transaction_id": 6,
  "reference": "TRX20240115143025ABC123",
  "new_balance": 13047.50
}
```

#### POST /transactions/withdrawal
Effectue un retrait sur un compte.

**Corps de la requête :**
```json
{
  "account_id": 1,
  "amount": 100.00,
  "description": "Retrait DAB"
}
```

**Réponse (201) :**
```json
{
  "message": "Retrait effectué avec succès",
  "transaction_id": 7,
  "reference": "TRX20240115143125DEF456",
  "new_balance": 12947.50
}
```

#### POST /transactions/transfer
Effectue un virement vers un autre compte.

**Corps de la requête :**
```json
{
  "source_account_id": 1,
  "recipient_iban": "FR7612345678900000000002345",
  "amount": 200.00,
  "description": "Virement épargne",
  "recipient_name": "Compte Épargne"
}
```

**Réponse (201) :**
```json
{
  "message": "Virement effectué avec succès",
  "reference": "TRX20240115143225GHI789",
  "new_balance": 12747.50,
  "amount_transferred": 200.00
}
```

#### POST /transactions/payment
Effectue un paiement.

**Corps de la requête :**
```json
{
  "account_id": 1,
  "merchant": "Supermarché Carrefour",
  "amount": 85.50,
  "category": "alimentation"
}
```

**Réponse (201) :**
```json
{
  "message": "Paiement effectué avec succès",
  "transaction_id": 8,
  "reference": "TRX20240115143325JKL012",
  "new_balance": 12662.00
}
```

## Codes d'Erreur

- **400 Bad Request**: Paramètres invalides ou manquants
- **401 Unauthorized**: Token absent ou invalide
- **403 Forbidden**: Accès refusé (compte désactivé)
- **404 Not Found**: Ressource non trouvée
- **409 Conflict**: Conflit (ex: email déjà existant)
- **500 Internal Server Error**: Erreur serveur

**Format de réponse d'erreur :**
```json
{
  "error": "Message d'erreur descriptif"
}
```

## Catégories de Transactions

- `alimentation`: Alimentation
- `logement`: Logement
- `transport`: Transport
- `loisirs`: Loisirs
- `sante`: Santé
- `shopping`: Shopping
- `services`: Services
- `salary`: Salaire
- `refund`: Remboursement
- `autres`: Autres

## Types de Transactions

- `deposit`: Dépôt
- `withdrawal`: Retrait
- `transfer_out`: Virement envoyé
- `transfer_in`: Virement reçu
- `payment`: Paiement
- `interest`: Intérêts
- `fee`: Frais
