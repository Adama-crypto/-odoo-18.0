# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = 'Configuration des alertes'
    _order = 'type, name'

    name = fields.Char(string='Nom', required=True)
    type = fields.Selection([
        ('garantie', 'Garantie équipement'),
        ('contrat', 'Contrat fournisseur'),
    ], string='Type d\'alerte', required=True)
    
    delai_jours = fields.Integer(string='Délai (jours)', required=True, default=30, help='Nombre de jours avant expiration pour déclencher l\'alerte')
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
    
    # Statistiques
    nombre_alertes_actives = fields.Integer(string='Alertes actives', compute='_compute_nombre_alertes_actives')

    @api.depends('active')
    def _compute_nombre_alertes_actives(self):
        for alerte in self:
            if alerte.active:
                if alerte.type == 'garantie':
                    alerte.nombre_alertes_actives = self.env['it.equipement'].search_count([
                        ('date_garantie', '>=', fields.Date.today()),
                        ('date_garantie', '<=', fields.Date.today() + timedelta(days=alerte.delai_jours)),
                    ])
                elif alerte.type == 'contrat':
                    alerte.nombre_alertes_actives = self.env['it.contrat'].search_count([
                        ('date_fin', '>=', fields.Date.today()),
                        ('date_fin', '<=', fields.Date.today() + timedelta(days=alerte.delai_jours)),
                        ('state', '=', 'actif'),
                    ])
            else:
                alerte.nombre_alertes_actives = 0

    def action_scanner_alertes(self):
        """Scanner les alertes manuellement"""
        self.ensure_one()
        alertes = self._get_alertes()
        return {
            'name': _('Résultat du scan'),
            'type': 'ir.actions.act_window',
            'res_model': 'it.scan.alertes.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_alerte_id': self.id,
                'default_resultat_ids': [(6, 0, alertes.ids)] if alertes else [],
            }
        }

    def _get_alertes(self):
        """Retourne les enregistrements concernés par l'alerte"""
        self.ensure_one()
        if not self.active:
            return self.env[self._get_model_name()]
        
        date_limite = fields.Date.today() + timedelta(days=self.delai_jours)
        
        if self.type == 'garantie':
            return self.env['it.equipement'].search([
                ('date_garantie', '>=', fields.Date.today()),
                ('date_garantie', '<=', date_limite),
            ])
        elif self.type == 'contrat':
            return self.env['it.contrat'].search([
                ('date_fin', '>=', fields.Date.today()),
                ('date_fin', '<=', date_limite),
                ('state', '=', 'actif'),
            ])
        return self.env[self._get_model_name()]

    def _get_model_name(self):
        """Retourne le nom du modèle concerné"""
        if self.type == 'garantie':
            return 'it.equipement'
        elif self.type == 'contrat':
            return 'it.contrat'
        # Retourner un modèle valide par défaut pour éviter env[False]
        return 'it.equipement'

    @api.model
    def cron_scan_alertes(self):
        """Tâche planifiée pour scanner automatiquement les alertes"""
        alertes_actives = self.search([('active', '=', True)])
        for alerte in alertes_actives:
            enregistrements = alerte._get_alertes()
            if enregistrements:
                # Créer un log
                log = self.env['it.alerte.log'].create({
                    'alerte_id': alerte.id,
                    'date_scan': fields.Datetime.now(),
                    'nombre_alertes': len(enregistrements),
                    'message': f"{len(enregistrements)} alerte(s) détectée(s) pour {alerte.name}",
                })
                
                # Envoyer une notification interne aux IT Managers
                group_manager = self.env.ref('it_parc.group_it_manager', raise_if_not_found=False)
                if group_manager:
                    users = group_manager.users
                    for user in users:
                        self.env['mail.message'].create({
                            'message_type': 'notification',
                            'subtype_id': self.env.ref('mail.mt_note').id,
                            'body': (
                                f"<b>🚨 Alerte IT : {alerte.name}</b><br/>"
                                f"{len(enregistrements)} élément(s) à traiter avant {alerte.delai_jours} jours.<br/>"
                                f"Type : {dict(self._fields['type'].selection).get(alerte.type, alerte.type)}"
                            ),
                            'author_id': self.env.ref('base.partner_root').id,
                            'partner_ids': [(4, user.partner_id.id)],
                            'model': 'it.alerte',
                            'res_id': alerte.id,
                        })


class ItAlerteLog(models.Model):
    _name = 'it.alerte.log'
    _description = 'Historique des scans d\'alertes'
    _order = 'date_scan desc'

    alerte_id = fields.Many2one('it.alerte', string='Alerte', required=True, ondelete='cascade')
    date_scan = fields.Datetime(string='Date du scan', required=True, default=fields.Datetime.now)
    nombre_alertes = fields.Integer(string='Nombre d\'alertes', required=True)
    message = fields.Text(string='Message')
