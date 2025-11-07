# Application Bancaire - MAMP Stack

Application bancaire complète développée avec MAMP, Apache, MySQL, Python Flask et modules C/C++.

## 📦 Stack Technologique

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Base de données**: MySQL
- **Serveur**: Apache (MAMP)
- **Modules natifs**: C/C++ pour le chiffrement

## 🚀 Installation Rapide

### Prérequis

- MAMP installé (macOS/Windows)
- Python 3.8+
- OpenSSL pour les modules C

### Étape 1: Cloner le repository

```bash
git clone https://github.com/tamalou25/banking-app-mamp.git
cd banking-app-mamp
```

### Étape 2: Installer les dépendances Python

```bash
cd backend
pip3 install -r requirements.txt
```

### Étape 3: Configurer MySQL dans MAMP

1. Démarrez MAMP
2. Ouvrez phpMyAdmin (http://localhost:8888/phpMyAdmin/)
3. Créez une base de données `banking_system`
4. Importez `database/schema.sql`
5. Importez `database/seed_data.sql`

### Étape 4: Configuration de l'environnement

Créez un fichier `.env` dans le dossier `backend/` :

```env
SECRET_KEY=votre-cle-secrete-changez-moi
JWT_SECRET_KEY=votre-jwt-secret-changez-moi
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=banking_system
FLASK_ENV=development
FLASK_DEBUG=True
```

### Étape 5: Lancer l'application

```bash
cd backend
python3 app.py
```

L'API sera disponible sur `http://localhost:5000`

### Étape 6: Accéder au frontend

Copiez le dossier dans MAMP htdocs :

```bash
cp -r . /Applications/MAMP/htdocs/banking-app
```

Accédez à `http://localhost:8888/banking-app/frontend/index.html`

## 👤 Compte de Test

- **Email**: jean.dupont@example.com
- **Mot de passe**: TestPassword123!

## 📚 Fonctionnalités

- ✅ Authentification JWT sécurisée
- ✅ Gestion multi-comptes (courant, épargne)
- ✅ Dépôts et retraits
- ✅ Virements IBAN
- ✅ Paiements catégorisés
- ✅ Historique des transactions
- ✅ Objectifs d'épargne
- ✅ Statistiques mensuelles
- ✅ Mode sombre automatique
- ✅ Responsive design

## 🛡️ Sécurité

- Hachage bcrypt pour les mots de passe
- Tokens JWT avec expiration
- Validation stricte des entrées
- Transactions atomiques MySQL
- Protection contre les injections SQL
- Module C pour chiffrement AES-256

## 📝 API Documentation

Consultez `docs/API_DOCUMENTATION.md` pour la documentation complète de l'API.

## ⚠️ Avertissement

Ceci est une application de **test/démonstration**. Ne l'utilisez PAS en production sans :

- Audit de sécurité complet
- Conformité réglementaire (RGPD, DSP2, PCI-DSS)
- Tests de pénétration
- HTTPS avec certificats SSL/TLS valides
- Rate limiting et protection DDoS

## 📝 Licence

MIT License - Voir LICENSE pour plus de détails

## 👥 Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou soumettez une pull request.
