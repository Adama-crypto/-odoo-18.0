# -*- coding: utf-8 -*-
{
    'name': 'IT Parc - Gestion du Parc Informatique',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Gestion complète du parc informatique pour TECHPARK CI',
    'description': """
Module de gestion du parc informatique pour TECHPARK CI
=====================================================

Fonctionnalités principales :
- Gestion des équipements (PCs, serveurs, imprimantes, réseau, téléphones IP)
- Affectation aux employés avec traçabilité complète
- Suivi des interventions de maintenance
- Gestion des contrats fournisseurs
- Alertes automatiques sur garanties et contrats
- Import CSV en masse
- Rapports PDF et exports Excel
- Dashboard temps réel pour la DSI
    """,
    'author': 'TECHPARK CI',
    # 'website': 'https://www.techpark.ci',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'stock',
        'purchase',
        'account',
        'maintenance',
        'mail',
        'contacts',
        'web',
    ],
    'data': [
        'security/it_parc_security.xml',
        'security/ir.model.access.csv',
        'data/it_parc_data.xml',
        'data/ir_cron.xml',
        'views/it_equipement_views.xml',
        'views/it_affectation_views.xml',
        'views/it_intervention_views.xml',
        'views/it_contrat_views.xml',
        'views/it_alerte_views.xml',
        'views/it_parc_menu.xml',
        'views/it_dashboard_views.xml',
        'wizards/it_reaffectation_wizard_views.xml',
        'wizards/it_renouvellement_contrat_wizard_views.xml',
        'wizards/it_import_csv_wizard_views.xml',
        'wizards/it_scan_alertes_wizard_views.xml',
        'report/it_equipement_report.xml',
        'report/it_inventaire_report.xml',
        'report/it_maintenance_report.xml',
        'data/it_parc_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'it_parc/static/src/dashboard/dashboard.js',
            'it_parc/static/src/dashboard/dashboard.xml',
            'it_parc/static/src/dashboard/dashboard.scss',
        ],
    },
    'demo': [
        'data/it_parc_demo.xml',
    ],
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook',
}
