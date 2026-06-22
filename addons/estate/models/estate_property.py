from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        default=lambda self: fields.Date.today() + relativedelta(months=3),
        copy=False
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('North', 'North'),
        ('South', 'South'),
        ('East', 'East'),
        ('West', 'West'),
    ])
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('New', 'New'),
        ('Offer Received', 'Offer Received'),
        ('Offer Accepted', 'Offer Accepted'),
        ('Sold', 'Sold'),
        ('Cancelled', 'Cancelled'),
        ('Libre', 'Libre'),
        ('Occupée', 'Occupée'),
        ('Réservée', 'Réservée'),
    ], required=True, default='New', copy=False)

    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    room_ids = fields.One2many('estate.room', 'property_id', string='Pièces')

    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_price')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'North'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive.')
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if not fields.Float.is_zero(record.selling_price, precision_digits=2) and record.expected_price:
                if record.selling_price < record.expected_price * 0.9:
                    raise ValidationError("The selling price cannot be lower than 90% of the expected price.")

    def action_sold(self):
        for record in self:
            if record.state == 'Cancelled':
                raise UserError("Cancelled properties cannot be sold.")
            record.state = 'Sold'
        return True

    def action_cancel(self):
        for record in self:
            if record.state == 'Sold':
                raise UserError("Sold properties cannot be cancelled.")
            record.state = 'Cancelled'
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        if any(property.state not in ('New', 'Cancelled') for property in self):
            raise UserError("You can only delete properties in 'New' or 'Cancelled' states.")
