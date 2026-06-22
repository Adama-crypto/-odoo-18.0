# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import odoo
import odoo.modules.registry as registry
import odoo.tools.config as config

config.parse_config(['-c', 'odoo.conf'])

reg = registry.Registry.new('test_it_parc')
with reg.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    
    # Supprimer l'équipement SN123456789 s'il existe
    existing = env['it.equipement'].search([('numero_serie', '=', 'SN123456789')])
    if existing:
        print(f"Trouvé {len(existing)} équipement(s) avec numéro de série SN123456789. Suppression...")
        existing.unlink()
        cr.commit()
        print("Suppression réussie et base de données nettoyée !")
    else:
        print("Aucun équipement en conflit trouvé.")
