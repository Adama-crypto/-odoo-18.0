# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ItReaffectationWizard(models.TransientModel):
    _name = 'it.reaffectation.wizard'
    _description = 'Wizard de réaffectation d\'équipement'

    equipement_id = fields.Many2one('it.equipement', string='Équipement', required=True, readonly=True)
    ancien_employe_id = fields.Many2one('hr.employee', string='Ancien employé', readonly=True)
    nouvel_employe_id = fields.Many2one('hr.employee', string='Nouvel employé', required=True)
    date_debut = fields.Date(string='Date de début', required=True, default=fields.Date.today())
    motif = fields.Text(string='Motif de la réaffectation', required=True)

    def action_confirmer(self):
        """Confirmer la réaffectation"""
        self.ensure_one()
        
        # Clôturer l'affectation actuelle
        ancienne_affectation = self.env['it.affectation'].search([
            ('equipement_id', '=', self.equipement_id.id),
            ('employe_id', '=', self.ancien_employe_id.id),
            ('active', '=', True),
        ], limit=1)
        
        if ancienne_affectation:
            ancienne_affectation.write({
                'date_fin': self.date_debut,
                'motif': self.motif,
                'active': False,
            })
        
        # Créer la nouvelle affectation
        self.env['it.affectation'].create({
            'equipement_id': self.equipement_id.id,
            'employe_id': self.nouvel_employe_id.id,
            'date_debut': self.date_debut,
            'motif': self.motif,
            'active': True,
        })
        
        # Mettre à jour l'équipement
        self.equipement_id.write({
            'employe_id': self.nouvel_employe_id.id,
            'departement_id': self.nouvel_employe_id.department_id.id,
            'state': 'affecte',
        })
        
        return {'type': 'ir.actions.act_window_close'}
