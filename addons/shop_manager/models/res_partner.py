from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shop_order_ids = fields.One2many(
        'shop.order',
        'partner_id',
        string='Commandes'
    )
    shop_invoice_ids = fields.One2many(
        'account.move',
        'partner_id',
        string='Factures',
        domain=[('move_type', '=', 'out_invoice')]
    )