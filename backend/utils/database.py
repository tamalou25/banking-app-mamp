# backend/utils/database.py
import mysql.connector
from mysql.connector import pooling
from flask import g, current_app

# Pool de connexions MySQL
connection_pool = None

def init_db(app):
    """Initialise le pool de connexions à la base de données"""
    global connection_pool
    
    try:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="banking_pool",
            pool_size=5,
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE'],
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            autocommit=False
        )
        print("✓ Connexion à MySQL établie avec succès")
    except mysql.connector.Error as err:
        print(f"✗ Erreur de connexion à MySQL: {err}")
        raise

def get_db_connection():
    """Obtient une connexion depuis le pool"""
    if 'db_connection' not in g:
        g.db_connection = connection_pool.get_connection()
    return g.db_connection

def close_db_connection(e=None):
    """Ferme la connexion à la base de données"""
    connection = g.pop('db_connection', None)
    if connection is not None:
        connection.close()

def execute_query(query, params=None, fetch=True, commit=False):
    """
    Exécute une requête SQL avec gestion d'erreurs
    
    Args:
        query: Requête SQL à exécuter
        params: Paramètres de la requête (tuple ou dict)
        fetch: Si True, retourne les résultats (SELECT)
        commit: Si True, commit la transaction (INSERT/UPDATE/DELETE)
    
    Returns:
        Résultats de la requête ou ID du dernier insert
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if commit:
            connection.commit()
            return cursor.lastrowid
        
        if fetch:
            results = cursor.fetchall()
            return results
        
        return None
        
    except mysql.connector.Error as err:
        if commit:
            connection.rollback()
        raise err
    finally:
        cursor.close()

def execute_many(query, data_list):
    """
    Exécute une requête avec plusieurs ensembles de paramètres
    Utile pour les insertions multiples
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.executemany(query, data_list)
        connection.commit()
        return cursor.rowcount
    except mysql.connector.Error as err:
        connection.rollback()
        raise err
    finally:
        cursor.close()
