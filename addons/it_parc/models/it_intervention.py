# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention de maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc, id'

    name = fields.Char(string='Référence', required=True, copy=False, default=lambda self: _('Nouvelle'))
    equipement_id = fields.Many2one('it.equipement', string='Équipement', required=True, tracking=True, ondelete='cascade')
    technicien_id = fields.Many2one('hr.employee', string='Technicien', required=True, tracking=True)
    
    type_intervention = fields.Selection([
        ('preventive', 'Préventive'),
        ('curative', 'Curative'),
        ('upgrade', 'Mise à niveau'),
        ('autre', 'Autre'),
    ], string='Type d\'intervention', required=True, default='curative', tracking=True)
    
    priorite = fields.Selection([
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('critique', 'Critique'),
    ], string='Priorité', required=True, default='normale', tracking=True)
    
    date_debut = fields.Datetime(string='Date de début', required=True, default=fields.Datetime.now, tracking=True)
    date_fin = fields.Datetime(string='Date de fin', tracking=True)
    duree_heures = fields.Float(string='Durée (heures)', compute='_compute_duree_heures', store=True)
    
    description = fields.Text(string='Description du problème', required=True)
    rapport = fields.Text(string='Rapport d\'intervention')
    
    cout = fields.Float(string='Coût (FCFA)', digits='Product Price')
    pieces_remplacees = fields.Text(string='Pièces remplacées')
    
    state = fields.Selection([
        ('planifie', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminée'),
        ('annule', 'Annulée'),
    ], string='État', default='planifie', required=True, tracking=True)
    
    notes = fields.Text(string='Notes')

    @api.depends('date_debut', 'date_fin')
    def _compute_duree_heures(self):
        for intervention in self:
            if intervention.date_debut and intervention.date_fin:
                delta = intervention.date_fin - intervention.date_debut
                intervention.duree_heures = delta.total_seconds() / 3600
            else:
                intervention.duree_heures = 0.0

    @api.constrains('date_fin', 'date_debut')
    def _check_dates(self):
        for intervention in self:
            if intervention.date_fin and intervention.date_fin < intervention.date_debut:
                raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle')) == _('Nouvelle'):
                vals['name'] = self.env['ir.sequence'].next_by_code('it.intervention') or _('Nouvelle')
        return super(ItIntervention, self).create(vals_list)

    def action_demarrer(self):
        """Démarrer l'intervention"""
        self.ensure_one()
        self.state = 'en_cours'
        self.date_debut = fields.Datetime.now()

    def action_terminer(self):
        """Terminer l'intervention"""
        self.ensure_one()
        if not self.date_fin:
            self.date_fin = fields.Datetime.now()
        self.state = 'termine'
        # Mettre l'équipement à jour si nécessaire
        if self.equipement_id.state == 'maintenance':
            self.equipement_id.state = 'affecte' if self.equipement_id.employe_id else 'brouillon'

    def action_annuler(self):
        """Annuler l'intervention"""
        self.ensure_one()
        self.state = 'annule'
