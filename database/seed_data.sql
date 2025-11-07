-- Données de test pour l'application bancaire
-- Utilisation: mysql -u root -p banking_system < seed_data.sql

USE banking_system;

-- Utilisateur de test (mot de passe: TestPassword123!)
-- Hash bcrypt généré pour le mot de passe 'TestPassword123!'
INSERT INTO users (email, username, password_hash, first_name, last_name, phone_number, date_of_birth, address)
VALUES (
    'jean.dupont@example.com',
    'jeandupont',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lW.5K9ow8Jm2',
    'Jean',
    'Dupont',
    '+33612345678',
    '1985-05-15',
    '123 Rue de la République, 75001 Paris, France'
);

-- Comptes bancaires de test
INSERT INTO accounts (user_id, account_number, account_type, balance, iban, overdraft_limit, interest_rate)
VALUES 
(1, '00000000001', 'courant', 12547.50, 'FR7612345678900000000001234', 500.00, 0.0000),
(1, '00000000002', 'epargne', 3300.00, 'FR7612345678900000000002345', 0.00, 0.0200);

-- Transactions de test
INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, category, reference_number)
VALUES
(1, 'deposit', 3200.00, 12547.50, 'Salaire - Entreprise ABC', 'salary', 'TRX001'),
(1, 'withdrawal', 950.00, 11597.50, 'Loyer - Agence Immobilière', 'logement', 'TRX002'),
(1, 'payment', 127.45, 11470.05, 'Supermarché Carrefour', 'alimentation', 'TRX003'),
(1, 'payment', 13.49, 11456.56, 'Netflix - Abonnement', 'loisirs', 'TRX004'),
(1, 'deposit', 85.00, 11541.56, 'Remboursement - Assurance', 'refund', 'TRX005');

-- Objectifs d'épargne
INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
VALUES
(1, 'Vacances d\'\u00e9té', 5000.00, 3300.00, '2026-07-01'),
(1, 'Nouvelle voiture', 20000.00, 8500.00, '2027-12-31');
