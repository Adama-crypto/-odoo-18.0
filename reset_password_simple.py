# -*- coding: utf-8 -*-
import psycopg2
from passlib.context import CryptContext

# Configuration de la base de données
db_name = 'didi_db'
db_user = 'postgres'
db_password = 'postgres'
db_host = 'localhost'
db_port = '5433'

# Nouveau mot de passe
new_password = 'admin123'

# Contexte de cryptage (compatible avec Odoo)
pwd_context = CryptContext(
    schemes=['pbkdf2_sha512'],
    default='pbkdf2_sha512',
)

# Crypter le mot de passe
hashed_password = pwd_context.hash(new_password)

# Connexion à la base de données
try:
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cursor = conn.cursor()
    
    # Mettre à jour le mot de passe de l'admin
    cursor.execute("""
        UPDATE res_users 
        SET password = %s 
        WHERE login = 'admin'
    """, (hashed_password,))
    
    # Mettre à jour l'email via la table res_partner
    cursor.execute("""
        UPDATE res_partner 
        SET email = %s 
        WHERE id IN (SELECT partner_id FROM res_users WHERE login = 'admin')
    """, ('didicarter3@gmail.com',))
    
    conn.commit()
    print(f"Mot de passe réinitialisé avec succès pour l'utilisateur admin")
    print(f"Nouveau mot de passe: {new_password}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erreur: {e}")
