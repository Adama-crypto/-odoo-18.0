# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ItEquipement(models.Model):
    _name = 'it.equipement'
    _description = 'Équipement Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, id'

    name = fields.Char(string='Nom / Référence', required=True, tracking=True)
    numero_serie = fields.Char(string='Numéro de série', required=True, tracking=True, copy=False)
    categorie_id = fields.Many2one('it.equipement.categorie', string='Catégorie', required=True, tracking=True)
    marque = fields.Char(string='Marque', tracking=True)
    modele = fields.Char(string='Modèle', tracking=True)
    
    # Caractéristiques techniques
    processeur = fields.Char(string='Processeur')
    ram = fields.Char(string='RAM')
    disque_dur = fields.Char(string='Disque dur')
    systeme_exploitation = fields.Char(string='Système d\'exploitation')
    adresse_mac = fields.Char(string='Adresse MAC')
    adresse_ip = fields.Char(string='Adresse IP')
    
    # Informations financières
    date_achat = fields.Date(string='Date d\'achat', tracking=True)
    prix_achat = fields.Float(string='Prix d\'achat (FCFA)', digits='Product Price')
    date_garantie = fields.Date(string='Date fin de garantie', tracking=True)
    fournisseur_id = fields.Many2one('res.partner', string='Fournisseur', domain=[('supplier_rank', '>', 0)])
    
    # Statut et localisation
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('affecte', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retire', 'Retiré'),
    ], string='État', default='brouillon', required=True, tracking=True)
    
    site_id = fields.Many2one('it.site', string='Site', required=True, tracking=True)
    departement_id = fields.Many2one('hr.department', string='Département')
    employe_id = fields.Many2one('hr.employee', string='Employé actuel', tracking=True)
    
    # Notes
    notes = fields.Text(string='Notes')
    image = fields.Binary(string='Image')
    
    # Relations
    affectation_ids = fields.One2many('it.affectation', 'equipement_id', string='Historique des affectations')
    intervention_ids = fields.One2many('it.intervention', 'equipement_id', string='Interventions')
    contrat_ids = fields.Many2many('it.contrat', 'it_contrat_equipement_rel', 'equipement_id', 'contrat_id', string='Contrats')
    
    # Calculés
    age_jours = fields.Integer(string='Âge (jours)', compute='_compute_age_jours', store=True)
    garantie_expire = fields.Boolean(string='Garantie expirée', compute='_compute_garantie_expire', store=True)
    jours_garantie_restants = fields.Integer(string='Jours garantie restants', compute='_compute_jours_garantie_restants')
    nombre_interventions = fields.Integer(string='Nombre d\'interventions', compute='_compute_nombre_interventions')
    cout_total_maintenance = fields.Float(string='Coût total maintenance', compute='_compute_cout_total_maintenance')
    
    _sql_constraints = [
        ('numero_serie_unique', 'UNIQUE(numero_serie)', 'Le numéro de série doit être unique !'),
    ]

    @api.depends('date_achat')
    def _compute_age_jours(self):
        for equip in self:
            if equip.date_achat:
                equip.age_jours = (fields.Date.today() - equip.date_achat).days
            else:
                equip.age_jours = 0

    @api.depends('date_garantie')
    def _compute_garantie_expire(self):
        for equip in self:
            equip.garantie_expire = equip.date_garantie and equip.date_garantie < fields.Date.today()

    @api.depends('date_garantie')
    def _compute_jours_garantie_restants(self):
        for equip in self:
            if equip.date_garantie:
                delta = equip.date_garantie - fields.Date.today()
                equip.jours_garantie_restants = delta.days if delta.days > 0 else 0
            else:
                equip.jours_garantie_restants = 0

    @api.depends('intervention_ids')
    def _compute_nombre_interventions(self):
        for equip in self:
            equip.nombre_interventions = len(equip.intervention_ids)

    @api.depends('intervention_ids.cout')
    def _compute_cout_total_maintenance(self):
        for equip in self:
            equip.cout_total_maintenance = sum(equip.intervention_ids.mapped('cout'))

    @api.constrains('date_garantie', 'date_achat')
    def _check_dates(self):
        for equip in self:
            if equip.date_garantie and equip.date_achat and equip.date_garantie < equip.date_achat:
                raise ValidationError(_('La date de fin de garantie doit être postérieure à la date d\'achat.'))

    def action_affecter(self):
        """Action pour affecter l'équipement"""
        self.ensure_one()
        return {
            'name': _('Affecter l\'équipement'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.affectation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_equipement_id': self.id,
                'default_date_debut': fields.Date.today(),
            }
        }

    def action_maintenance(self):
        """Action pour mettre en maintenance"""
        self.ensure_one()
        self.state = 'maintenance'

    def action_retirer(self):
        """Action pour retirer l'équipement"""
        self.ensure_one()
        if self.employe_id:
            # Créer une affectation de fin
            self.env['it.affectation'].create({
                'equipement_id': self.id,
                'employe_id': self.employe_id.id,
                'date_debut': self.affectation_ids.filtered(lambda a: a.active).date_debut,
                'date_fin': fields.Date.today(),
                'motif': 'Retrait du parc',
                'active': False,
            })
            self.employe_id = False
        self.state = 'retire'

    def action_reactiver(self):
        """Action pour réactiver l'équipement"""
        self.ensure_one()
        self.state = 'brouillon'

    def action_reaffecter(self):
        """Action pour réaffecter l'équipement"""
        self.ensure_one()
        return {
            'name': _('Réaffecter l\'équipement'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.reaffectation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_equipement_id': self.id,
                'default_ancien_employe_id': self.employe_id.id if self.employe_id else False,
            }
        }


class ItEquipementCategorie(models.Model):
    _name = 'it.equipement.categorie'
    _description = 'Catégorie d\'équipement'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string='Description')
    code = fields.Char(string='Code')


class ItSite(models.Model):
    _name = 'it.site'
    _description = 'Site'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    adresse = fields.Text(string='Adresse')
    ville = fields.Char(string='Ville')
    pays_id = fields.Many2one('res.country', string='Pays')
    telephone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
