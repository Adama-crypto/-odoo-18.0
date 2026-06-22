from odoo import models, fields

class EstateIntervention(models.Model):
    _name = 'estate.intervention'
    _description = 'Interventions'

    name = fields.Char(string='Référence', required=True, copy=False, default='Nouvelle intervention')
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    type = fields.Char(string='Type', required=True)
    property_id = fields.Many2one('estate.property', string='Propriété', required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée')
    ], string='Statut', default='planned', required=True)
