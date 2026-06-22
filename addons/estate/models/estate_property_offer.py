from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(required=True)
    status = fields.Selection([
        ('Accepted', 'Accepted'),
        ('Refused', 'Refused'),
    ], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    property_type_id = fields.Many2one('estate.property.type', related='property_id.property_type_id', store=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The offer price must be strictly positive.')
    ]

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = (record.date_deadline - create_date).days

    def action_accept(self):
        for record in self:
            if record.status == 'Accepted':
                continue
            if 'Accepted' in record.property_id.offer_ids.mapped('status'):
                raise UserError("Only one offer can be accepted.")
            record.status = 'Accepted'
            record.property_id.write({
                'selling_price': record.price,
                'buyer_id': record.partner_id.id,
                'state': 'Offer Accepted'
            })
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'Refused'
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_obj = self.env['estate.property'].browse(vals.get('property_id'))
            if property_obj.best_price and vals.get('price') and vals['price'] < property_obj.best_price:
                raise UserError("You cannot create an offer with a lower price than the best offer.")
            property_obj.state = 'Offer Received'
        return super().create(vals_list)
