# -*- coding: utf-8 -*-
import sys
import os

# Ajouter le chemin d'Odoo au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import odoo
from odoo import api, SUPERUSER_ID

# Configuration
db_name = 'odoo'
new_password = 'admin123'  # Nouveau mot de passe

# Réinitialiser le mot de passe
with odoo.api.Environment.manage():
    registry = odoo.modules.registry.Registry(db_name)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        # Réinitialiser le mot de passe de l'admin
        admin_user = env['res.users'].search([('login', '=', 'admin')], limit=1)
        if admin_user:
            admin_user.write({'password': new_password})
            print(f"Mot de passe réinitialisé pour l'utilisateur admin: {new_password}")
        else:
            # Créer l'utilisateur admin s'il n'existe pas
            env['res.users'].create({
                'name': 'Administrator',
                'login': 'admin',
                'password': new_password,
                'email': 'admin@example.com',
                'groups_id': [(6, 0, [env.ref('base.group_system').id])]
            })
            print(f"Utilisateur admin créé avec le mot de passe: {new_password}")
