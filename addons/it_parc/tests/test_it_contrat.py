# -*- coding: utf-8 -*-

from odoo.tests import common
from datetime import date, timedelta


class TestItContrat(common.TransactionCase):
    """Tests pour le modèle it.contrat"""

    def setUp(self):
        super().setUp()
        self.Contrat = self.env['it.contrat']
        self.Partner = self.env['res.partner']

        # Créer un fournisseur de test
        self.fournisseur = self.Partner.create({
            'name': 'Fournisseur Test CI',
            'is_company': True,
        })

        # Contrat valide
        self.contrat = self.Contrat.create({
            'name': 'MAINT-TEST-001',
            'fournisseur_id': self.fournisseur.id,
            'type_contrat': 'maintenance',
            'date_debut': date.today(),
            'date_fin': date.today() + timedelta(days=365),
            'montant': 1000000,
        })

    def test_creation_contrat(self):
        """Test: un contrat est créé correctement"""
        self.assertEqual(self.contrat.name, 'MAINT-TEST-001')
        self.assertEqual(self.contrat.type_contrat, 'maintenance')

    def test_jours_restants_contrat(self):
        """Test: les jours restants sont calculés correctement"""
        jours = self.contrat.jours_restants
        self.assertGreater(jours, 300)
        self.assertLessEqual(jours, 366)

    def test_contrat_expire(self):
        """Test: un contrat expiré a des jours restants négatifs"""
        contrat_expire = self.Contrat.create({
            'name': 'MAINT-EXPIRE-001',
            'fournisseur_id': self.fournisseur.id,
            'type_contrat': 'support',
            'date_debut': date.today() - timedelta(days=400),
            'date_fin': date.today() - timedelta(days=30),
            'montant': 500000,
        })
        self.assertLess(contrat_expire.jours_restants, 0)

    def test_type_contrat_values(self):
        """Test: les types de contrat acceptés sont valides"""
        types_valides = ['maintenance', 'licence', 'support']
        for type_val in types_valides:
            contrat = self.Contrat.create({
                'name': f'TEST-{type_val.upper()}',
                'fournisseur_id': self.fournisseur.id,
                'type_contrat': type_val,
                'date_debut': date.today(),
                'date_fin': date.today() + timedelta(days=365),
                'montant': 100000,
            })
            self.assertEqual(contrat.type_contrat, type_val)
