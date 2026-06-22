# -*- coding: utf-8 -*-
import psycopg2

# Configuration PostgreSQL
db_host = 'localhost'
db_port = '5433'
db_user = 'postgres'
db_password = 'postgres'
new_db_name = 'didi_db'

try:
    # Connexion à PostgreSQL (base de données par défaut postgres)
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.autocommit = True  # Nécessaire pour CREATE DATABASE
    cursor = conn.cursor()
    
    # Créer la base de données
    cursor.execute(f"CREATE DATABASE {new_db_name}")
    print(f"Base de données '{new_db_name}' créée avec succès")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erreur lors de la création de la base de données: {e}")
