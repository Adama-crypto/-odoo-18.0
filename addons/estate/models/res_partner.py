from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    rental_ids = fields.One2many('estate.rental', 'tenant_id', string='Locations')
