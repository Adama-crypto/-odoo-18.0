# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta


class ItRenouvellementContratWizard(models.TransientModel):
    _name = 'it.renouvellement.contrat.wizard'
    _description = 'Wizard de renouvellement de contrat'

    contrat_id = fields.Many2one('it.contrat', string='Contrat', required=True, readonly=True)
    date_debut = fields.Date(string='Nouvelle date de début', required=True)
    date_fin = fields.Date(string='Nouvelle date de fin', required=True)
    montant = fields.Float(string='Nouveau montant (FCFA)', required=True, digits='Product Price')
    notes = fields.Text(string='Notes')

    @api.onchange('contrat_id')
    def _onchange_contrat_id(self):
        if self.contrat_id:
            self.date_debut = self.contrat_id.date_fin + timedelta(days=1)
            self.date_fin = self.date_debut + timedelta(days=self.contrat_id.duree_jours)
            self.montant = self.contrat_id.montant

    def action_confirmer(self):
        """Confirmer le renouvellement"""
        self.ensure_one()
        
        # Marquer l'ancien contrat comme renouvelé (via la méthode qui utilise state_force)
        self.contrat_id.action_marquer_renouvele()
        
        # Créer le nouveau contrat
        nouveau_contrat = self.contrat_id.copy({
            'date_debut': self.date_debut,
            'date_fin': self.date_fin,
            'montant': self.montant,
            'state_force': False,  # Réinitialiser l'état forcé
            'name': f"{self.contrat_id.name}-R",
        })
        
        # Copier les équipements
        nouveau_contrat.write({
            'equipement_ids': [(6, 0, self.contrat_id.equipement_ids.ids)],
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.contrat',
            'res_id': nouveau_contrat.id,
            'view_mode': 'form',
            'target': 'current',
        }
