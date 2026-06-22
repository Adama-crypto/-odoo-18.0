# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class ItContrat(models.Model):
    _name = 'it.contrat'
    _description = 'Contrat fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_fin desc, id'

    name = fields.Char(string='Référence', required=True, tracking=True)
    fournisseur_id = fields.Many2one('res.partner', string='Fournisseur', required=True, tracking=True, domain=[('supplier_rank', '>', 0)])
    
    type_contrat = fields.Selection([
        ('maintenance', 'Maintenance'),
        ('licence', 'Licence'),
        ('support', 'Support'),
        ('autre', 'Autre'),
    ], string='Type de contrat', required=True, default='maintenance', tracking=True)
    
    date_debut = fields.Date(string='Date de début', required=True, tracking=True)
    date_fin = fields.Date(string='Date de fin', required=True, tracking=True)
    montant = fields.Float(string='Montant (FCFA)', required=True, digits='Product Price', tracking=True)
    
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    
    equipement_ids = fields.Many2many('it.equipement', 'it_contrat_equipement_rel', 'contrat_id', 'equipement_id', string='Équipements couverts')
    
    # Permet de forcer un état manuellement (annulé, renouvelé)
    state_force = fields.Selection([
        ('annule', 'Annulé'),
        ('renouvele', 'Renouvelé'),
    ], string='État forcé', default=False, tracking=True, copy=False)

    state = fields.Selection([
        ('actif', 'Actif'),
        ('expire', 'Expiré'),
        ('renouvele', 'Renouvelé'),
        ('annule', 'Annulé'),
    ], string='État', compute='_compute_state', store=True, tracking=True)
    
    # Calculés
    duree_jours = fields.Integer(string='Durée (jours)', compute='_compute_duree_jours', store=True)
    jours_restants = fields.Integer(string='Jours restants', compute='_compute_jours_restants')
    expire_bientot = fields.Boolean(string='Expire bientôt', compute='_compute_expire_bientot', store=True)
    
    _sql_constraints = [
        ('dates_check', 'CHECK(date_fin >= date_debut)', 'La date de fin doit être postérieure à la date de début.'),
    ]

    @api.depends('date_fin', 'state_force')
    def _compute_state(self):
        today = fields.Date.today()
        for contrat in self:
            # Si un état a été forcé manuellement, on le respecte
            if contrat.state_force:
                contrat.state = contrat.state_force
            elif contrat.date_fin and contrat.date_fin < today:
                contrat.state = 'expire'
            else:
                contrat.state = 'actif'

    @api.depends('date_debut', 'date_fin')
    def _compute_duree_jours(self):
        for contrat in self:
            if contrat.date_debut and contrat.date_fin:
                contrat.duree_jours = (contrat.date_fin - contrat.date_debut).days
            else:
                contrat.duree_jours = 0

    @api.depends('date_fin')
    def _compute_jours_restants(self):
        today = fields.Date.today()
        for contrat in self:
            if contrat.date_fin:
                delta = contrat.date_fin - today
                contrat.jours_restants = delta.days if delta.days > 0 else 0
            else:
                contrat.jours_restants = 0

    @api.depends('date_fin')
    def _compute_expire_bientot(self):
        today = fields.Date.today()
        for contrat in self:
            if contrat.date_fin:
                delta = contrat.date_fin - today
                contrat.expire_bientot = 0 < delta.days <= 60
            else:
                contrat.expire_bientot = False

    def action_renouveler(self):
        """Action pour renouveler le contrat"""
        self.ensure_one()
        return {
            'name': _('Renouveler le contrat'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.renouvellement.contrat.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contrat_id': self.id,
                'default_date_debut': self.date_fin + timedelta(days=1),
            }
        }

    def action_annuler(self):
        """Annuler le contrat"""
        self.ensure_one()
        self.state_force = 'annule'

    def action_marquer_renouvele(self):
        """Marquer le contrat comme renouvelé (appelé par le wizard de renouvellement)"""
        self.ensure_one()
        self.state_force = 'renouvele'
