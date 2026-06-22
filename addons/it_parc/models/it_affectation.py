# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItAffectation(models.Model):
    _name = 'it.affectation'
    _description = 'Affectation d\'équipement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc, id'

    equipement_id = fields.Many2one('it.equipement', string='Équipement', required=True, ondelete='cascade', tracking=True)
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, tracking=True)
    date_debut = fields.Date(string='Date de début', required=True, default=fields.Date.today(), tracking=True)
    date_fin = fields.Date(string='Date de fin', tracking=True)
    motif = fields.Text(string='Motif')
    active = fields.Boolean(string='Active', default=True, tracking=True)
    
    # Informations au moment de l'affectation
    site_id = fields.Many2one('it.site', string='Site', related='equipement_id.site_id', store=True, readonly=True)
    departement_id = fields.Many2one('hr.department', string='Département', related='employe_id.department_id', store=True, readonly=True)
    
    notes = fields.Text(string='Notes')

    @api.constrains('date_fin', 'date_debut')
    def _check_dates(self):
        for affectation in self:
            if affectation.date_fin and affectation.date_fin < affectation.date_debut:
                raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))

    def name_get(self):
        result = []
        for affectation in self:
            name = f"{affectation.equipement_id.name} → {affectation.employe_id.name}"
            if affectation.date_debut:
                name += f" ({affectation.date_debut})"
            result.append((affectation.id, name))
        return result
