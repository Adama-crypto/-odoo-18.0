import odoo
import odoo.modules.registry as registry
import odoo.tools.config as config

# Configure Odoo (use same config as your server)
config['db_name'] = 'didi_db'
config['addons_path'] = [
    'c:/Users/MSI/Downloads/odoo-18.0/odoo-18.0/odoo/addons',
    'c:/Users/MSI/Downloads/odoo-18.0/odoo-18.0/addons'
]
config['admin_passwd'] = 'admin'  # placeholder if needed

reg = registry.Registry.new('didi_db')
with reg.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    # Find admin user (login='admin')
    admin_user = env['res.users'].search([('login', '=', 'admin')], limit=1)
    if not admin_user:
        print('Admin user not found')
    else:
        # Get the Settings group (base.group_system)
        settings_group = env.ref('base.group_system')
        # Add user to the group if not already present
        admin_user.write({'groups_id': [(4, settings_group.id)]})
        print('Admin user granted Settings access')
