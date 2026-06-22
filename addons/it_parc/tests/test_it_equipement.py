# -*- coding: utf-8 -*-

from odoo.tests import common
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestItEquipement(common.TransactionCase):
    """Tests pour le modèle it.equipement"""

    def setUp(self):
        super().setUp()
        self.Equipement = self.env['it.equipement']
        self.Categorie = self.env['it.equipement.categorie']
        self.Site = self.env['it.site']

        # Créer une catégorie de test
        self.categorie = self.Categorie.create({
            'name': 'PC Portable Test',
            'code': 'TEST-LAPTOP',
        })

        # Créer un site de test
        self.site = self.Site.create({
            'name': 'Site Test',
            'ville': 'Abidjan',
        })

        # Créer un équipement de base
        self.equipement = self.Equipement.create({
            'name': 'TEST-001',
            'numero_serie': 'SN-TEST-001',
            'categorie_id': self.categorie.id,
            'site_id': self.site.id,
            'prix_achat': 500000,
            'date_achat': date.today() - timedelta(days=365),
            'date_garantie': date.today() + timedelta(days=30),
        })

    def test_creation_equipement(self):
        """Test: un équipement peut être créé avec les champs obligatoires"""
        self.assertEqual(self.equipement.name, 'TEST-001')
        self.assertEqual(self.equipement.numero_serie, 'SN-TEST-001')
        self.assertEqual(self.equipement.state, 'brouillon')

    def test_numero_serie_unique(self):
        """Test: deux équipements ne peuvent pas avoir le même numéro de série"""
        with self.assertRaises(Exception):
            self.Equipement.create({
                'name': 'TEST-002',
                'numero_serie': 'SN-TEST-001',  # Même numéro de série
                'categorie_id': self.categorie.id,
                'site_id': self.site.id,
            })

    def test_calcul_age(self):
        """Test: le calcul de l'âge de l'équipement est correct"""
        # L'équipement a été acheté il y a 365 jours => environ 1 an
        self.assertGreater(self.equipement.age, 0)

    def test_jours_garantie_restants(self):
        """Test: les jours de garantie restants sont calculés correctement"""
        # Garantie dans 30 jours
        jours = self.equipement.jours_garantie_restants
        self.assertGreater(jours, 0)
        self.assertLessEqual(jours, 31)

    def test_garantie_expiree(self):
        """Test: équipement avec garantie expirée"""
        self.equipement.write({
            'date_garantie': date.today() - timedelta(days=10),
        })
        self.assertLess(self.equipement.jours_garantie_restants, 0)

    def test_workflow_state(self):
        """Test: le workflow d'état fonctionne correctement"""
        self.assertEqual(self.equipement.state, 'brouillon')
