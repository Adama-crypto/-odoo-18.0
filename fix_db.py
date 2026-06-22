import logging
from odoo import api, SUPERUSER_ID

env = api.Environment(env.cr, SUPERUSER_ID, {})
views = env['ir.ui.view'].search([('arch_db', 'ilike', 'duplicate_bank_partner_ids')])
for view in views:
    print(f"Found broken view: {view.name} (ID: {view.id})")
    view.write({'active': False})
    print("View deactivated.")
env.cr.commit()
print("Done fixing database.")
