from odoo import models, fields, api, exceptions

class EstateRental(models.Model):
    _name = 'estate.rental'
    _description = 'Locations'

    tenant_id = fields.Many2one('res.partner', string='Locataire', required=True)
    property_id = fields.Many2one('estate.property', string='Propriété', required=True)
    reservation_date = fields.Date(string='Date de réservation', default=fields.Date.context_today)
    start_date = fields.Date(string='Date de début', required=True)
    end_date = fields.Date(string='Date de fin', required=True)
    duration = fields.Integer(string='Durée (jours)', compute='_compute_duration', store=True)
    payment_frequency = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('yearly', 'Annuelle')
    ], string='Fréquence de paiement', required=True, default='monthly')
    rent = fields.Float(string='Loyer', required=True)
    inventory_status = fields.Selection([
        ('pending', 'En attente'),
        ('done', 'Fait')
    ], string='États des lieux', default='pending')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validée'),
        ('in_progress', 'En cours'),
        ('cancelled', 'Annulée')
    ], string='Statut', default='draft', required=True)

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration = delta.days
            else:
                record.duration = 0

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date >= record.end_date:
                raise exceptions.ValidationError("La date de fin doit être postérieure à la date de début.")

    @api.constrains('property_id', 'state')
    def _check_property_availability(self):
        for record in self:
            if record.state in ['validated', 'in_progress'] and record.property_id.state == 'Occupée':
                raise exceptions.ValidationError("Vous ne pouvez pas louer une propriété déjà occupée.")

    @api.model_create_multi
    def create(self, vals_list):
        rentals = super().create(vals_list)
        for rental in rentals:
            if rental.state == 'in_progress':
                rental.property_id.state = 'Occupée'
            elif rental.state == 'validated':
                rental.property_id.state = 'Réservée'
        return rentals

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            for record in self:
                if record.state == 'in_progress':
                    record.property_id.state = 'Occupée'
                elif record.state == 'validated':
                    record.property_id.state = 'Réservée'
                elif record.state in ['draft', 'cancelled'] and record.property_id.state in ['Occupée', 'Réservée']:
                    record.property_id.state = 'Libre'
        return res
