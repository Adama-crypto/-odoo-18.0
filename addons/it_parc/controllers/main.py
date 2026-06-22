# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class ITDashboardController(http.Controller):

    @http.route('/it_parc/dashboard/data', type='json', auth='user')
    def dashboard_data(self):
        """Return data for the IT dashboard"""
        equipement = request.env['it.equipement']
        intervention = request.env['it.intervention']
        
        # KPIs
        total_equipements = equipement.search_count([])
        equipements_affectes = equipement.search_count([('state', '=', 'affecte')])
        equipements_maintenance = equipement.search_count([('state', '=', 'maintenance')])
        interventions_en_cours = intervention.search_count([('state', '=', 'en_cours')])
        
        # Équipements par catégorie
        equipements_par_categorie = []
        categories = request.env['it.equipement.categorie'].search([])
        for cat in categories:
            count = equipement.search_count([('categorie_id', '=', cat.id)])
            if count > 0:
                equipements_par_categorie.append({
                    'name': cat.name,
                    'count': count,
                })
        
        # Interventions par mois (derniers 6 mois)
        interventions_par_mois = []
        from datetime import datetime, timedelta
        for i in range(6):
            date_start = datetime.now().replace(day=1) - timedelta(days=i*30)
            date_end = date_start + timedelta(days=30)
            count = intervention.search_count([
                ('date_debut', '>=', date_start.strftime('%Y-%m-%d')),
                ('date_debut', '<', date_end.strftime('%Y-%m-%d')),
            ])
            interventions_par_mois.append({
                'month': date_start.strftime('%m/%Y'),
                'count': count,
            })
        interventions_par_mois.reverse()
        
        return {
            'total_equipements': total_equipements,
            'equipements_affectes': equipements_affectes,
            'equipements_maintenance': equipements_maintenance,
            'interventions_en_cours': interventions_en_cours,
            'equipements_par_categorie': equipements_par_categorie,
            'interventions_par_mois': interventions_par_mois,
        }
