from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_published = fields.Boolean(
        string='Visible sur le site web',
        default=True
    )

    @api.constrains('qty_available')
    def _check_qty_not_negative(self):
        for product in self:
            if product.qty_available < 0:
                raise models.ValidationError(
                    "Le stock d'un produit ne peut pas être négatif."
                )