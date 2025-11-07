# Guide d'Installation - Application Bancaire MAMP

## Prérequis

- **MAMP** (macOS) ou **MAMP pour Windows**
- **Python 3.8+**
- **OpenSSL** (pour les modules C optionnels)
- **Git** (pour cloner le repository)

## Étape 1: Installation de MAMP

### macOS

1. Téléchargez MAMP depuis [https://www.mamp.info](https://www.mamp.info)
2. Installez MAMP en suivant les instructions
3. Lancez MAMP et démarrez les serveurs Apache et MySQL

### Windows

1. Téléchargez MAMP pour Windows
2. Installez dans `C:\MAMP`
3. Lancez MAMP et démarrez les serveurs

## Étape 2: Cloner le Repository

```bash
cd /Applications/MAMP/htdocs  # macOS
cd C:\MAMP\htdocs              # Windows

git clone https://github.com/tamalou25/banking-app-mamp.git
cd banking-app-mamp
```

## Étape 3: Installation de Python et Dépendances

### Vérifier Python

```bash
python3 --version
```

Si Python n'est pas installé :

- **macOS**: `brew install python3` (avec Homebrew)
- **Windows**: Téléchargez depuis [python.org](https://www.python.org)

### Installer les dépendances

```bash
cd backend
pip3 install -r requirements.txt
```

Dépendances installées :
- Flask (framework web)
- Flask-CORS (gestion CORS)
- Flask-JWT-Extended (authentification)
- mysql-connector-python (connexion MySQL)
- bcrypt (hachage mots de passe)
- python-dotenv (variables d'environnement)

## Étape 4: Configuration de MySQL

### Accéder à phpMyAdmin

1. Ouvrez votre navigateur
2. Accédez à `http://localhost:8888/phpMyAdmin/`
3. Connectez-vous avec :
   - Utilisateur: `root`
   - Mot de passe: `root`

### Créer la base de données

#### Option A: Via phpMyAdmin (Recommandé)

1. Cliquez sur "Nouvelle base de données"
2. Nom: `banking_system`
3. Interclassement: `utf8mb4_unicode_ci`
4. Cliquez sur "Créer"

5. Sélectionnez la base `banking_system`
6. Cliquez sur l'onglet "Importer"
7. Choisissez le fichier `database/schema.sql`
8. Cliquez sur "Exécuter"

9. Répétez pour `database/seed_data.sql`

#### Option B: Via ligne de commande

```bash
# macOS
/Applications/MAMP/Library/bin/mysql -u root -p

# Windows
C:\MAMP\bin\mysql\bin\mysql.exe -u root -p
```

Entrez le mot de passe `root`, puis :

```sql
CREATE DATABASE banking_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE banking_system;
source database/schema.sql;
source database/seed_data.sql;
EXIT;
```

### Vérifier l'installation

Dans phpMyAdmin, vérifiez que les tables suivantes existent :
- users
- accounts
- transactions
- cards
- savings_goals
- user_sessions
- audit_logs

## Étape 5: Configuration de l'Environnement

### Créer le fichier .env

```bash
cd backend
cp .env.example .env
```

### Éditer le fichier .env

Ouvrez `backend/.env` et modifiez si nécessaire :

```env
SECRET_KEY=votre-cle-secrete-changez-moi-en-production
JWT_SECRET_KEY=votre-jwt-secret-changez-moi-en-production
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=banking_system
FLASK_ENV=development
FLASK_DEBUG=True
```

**⚠️ Important**: En production, changez les clés secrètes !

## Étape 6: Lancer l'Application

### Démarrer le serveur Flask

Dans un terminal :

```bash
cd backend
python3 app.py
```

Vous devriez voir :

```
✓ Connexion à MySQL établie avec succès
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Tester l'API

Dans un nouveau terminal :

```bash
curl http://localhost:5000/api/health
```

Réponse attendue :

```json
{"status":"healthy","message":"Banking API is running"}
```

### Accéder au Frontend

Ouvrez votre navigateur et accédez à :

```
http://localhost:8888/banking-app/frontend/login.html
```

### Connexion avec le compte de test

- **Email**: `jean.dupont@example.com`
- **Mot de passe**: `TestPassword123!`

## Étape 7: Vérification

### Frontend

✅ Page de connexion s'affiche  
✅ Connexion réussie avec le compte test  
✅ Dashboard affiche les comptes  
✅ Solde total affiché correctement  
✅ Transactions affichées  

### Backend

✅ API répond sur port 5000  
✅ Connexion MySQL fonctionnelle  
✅ JWT généré à la connexion  
✅ Transactions en base de données  

## Dépannage

### Erreur: "Module not found"

```bash
cd backend
pip3 install -r requirements.txt --upgrade
```

### Erreur: "Can't connect to MySQL"

Vérifiez que MySQL est démarré dans MAMP :

1. Ouvrez MAMP
2. Vérifiez que le voyant MySQL est vert
3. Vérifiez le port dans `.env` (3306 ou 8889)

### Erreur: "Access denied for user 'root'"

Vérifiez le mot de passe MySQL :

```bash
/Applications/MAMP/Library/bin/mysql -u root -p
```

Le mot de passe par défaut est `root`

### Erreur CORS

Assurez-vous que :

1. Flask-CORS est installé
2. Le backend est lancé sur port 5000
3. Le frontend accède via MAMP (port 8888)

### Page blanche

Ouvrez la console du navigateur (F12) et vérifiez :

1. Les erreurs JavaScript
2. Les erreurs réseau
3. Que l'API backend répond

## Configuration Apache (Optionnel)

Pour intégrer l'API dans Apache :

```bash
cp config/apache/banking-app.conf /Applications/MAMP/conf/apache/extra/
```

Éditez `/Applications/MAMP/conf/apache/httpd.conf` et ajoutez :

```apache
Include conf/extra/banking-app.conf
```

Redémarrez Apache depuis MAMP.

## Prochaines Étapes

✅ Application fonctionnelle en local  
□ Tester toutes les fonctionnalités  
□ Personnaliser les données de test  
□ Ajouter vos propres fonctionnalités  
□ Consulter la documentation API  

## Support

Pour toute question :

- Consultez la documentation dans `docs/`
- Ouvrez une issue sur GitHub
- Vérifiez les logs dans `backend/` et MAMP logs

## Avertissement Sécurité

⚠️ **Cette application est pour TEST/DÉMONSTRATION uniquement**

Ne PAS utiliser en production sans :

- Audit de sécurité complet
- HTTPS avec certificats SSL/TLS
- Clés secrètes robustes
- Rate limiting
- Protection DDoS
- Conformité réglementaire (RGPD, PCI-DSS)
- Tests de pénétration
