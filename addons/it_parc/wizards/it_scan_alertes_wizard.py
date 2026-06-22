# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ItScanAlertesWizard(models.TransientModel):
    _name = 'it.scan.alertes.wizard'
    _description = 'Wizard de scan d\'alertes'

    alerte_id = fields.Many2one('it.alerte', string='Alerte', required=True)
    resultat_ids = fields.Many2many('it.equipement', string='Équipements concernés')
    resultat_contrat_ids = fields.Many2many('it.contrat', string='Contrats concernés')
    message = fields.Text(string='Message', readonly=True)

    @api.onchange('alerte_id')
    def _onchange_alerte_id(self):
        if self.alerte_id:
            enregistrements = self.alerte_id._get_alertes()
            if self.alerte_id.type == 'garantie':
                self.resultat_ids = [(6, 0, enregistrements.ids)]
                self.resultat_contrat_ids = [(5, 0, 0)]
                self.message = f"{len(enregistrements)} équipement(s) avec garantie expirant dans {self.alerte_id.delai_jours} jours"
            elif self.alerte_id.type == 'contrat':
                self.resultat_contrat_ids = [(6, 0, enregistrements.ids)]
                self.resultat_ids = [(5, 0, 0)]
                self.message = f"{len(enregistrements)} contrat(s) expirant dans {self.alerte_id.delai_jours} jours"

    def action_envoyer_notification(self):
        """Envoyer une notification aux utilisateurs concernés"""
        self.ensure_one()
        
        # Envoyer un message aux managers IT
        managers = self.env.ref('it_parc.group_it_manager').users
        if managers:
            self.message_post(
                body=self.message,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids=managers.mapped('partner_id').ids
            )
        
        return {'type': 'ir.actions.act_window_close'}
