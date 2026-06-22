# -*- coding: utf-8 -*-

from odoo.tests import common
from datetime import datetime, timedelta


class TestItIntervention(common.TransactionCase):
    """Tests pour le modèle it.intervention"""

    def setUp(self):
        super().setUp()
        self.Intervention = self.env['it.intervention']
        self.Equipement = self.env['it.equipement']
        self.Categorie = self.env['it.equipement.categorie']
        self.Site = self.env['it.site']

        # Catégorie
        self.categorie = self.Categorie.create({
            'name': 'Serveur Test',
            'code': 'SRV-TEST',
        })

        # Site
        self.site = self.Site.create({
            'name': 'Site Intervention Test',
            'ville': 'Bouaké',
        })

        # Équipement
        self.equipement = self.Equipement.create({
            'name': 'SRV-TEST-001',
            'numero_serie': 'SN-SRV-TEST-001',
            'categorie_id': self.categorie.id,
            'site_id': self.site.id,
        })

        # Intervention
        now = datetime.now()
        self.intervention = self.Intervention.create({
            'equipement_id': self.equipement.id,
            'technicien_id': self.env.uid,
            'type_intervention': 'curative',
            'priorite': 'haute',
            'date_debut': now,
            'date_fin': now + timedelta(hours=2),
            'description': 'Test intervention curative',
            'cout': 75000,
        })

    def test_creation_intervention(self):
        """Test: une intervention est créée correctement"""
        self.assertEqual(self.intervention.type_intervention, 'curative')
        self.assertEqual(self.intervention.priorite, 'haute')
        self.assertEqual(self.intervention.state, 'planifie')

    def test_duree_calculee(self):
        """Test: la durée est calculée automatiquement"""
        # 2 heures = 120 minutes
        self.assertAlmostEqual(self.intervention.duree, 2.0, delta=0.1)

    def test_cout_positif(self):
        """Test: le coût ne peut pas être négatif"""
        self.assertGreaterEqual(self.intervention.cout, 0)

    def test_workflow_en_cours(self):
        """Test: passage à l'état 'en_cours'"""
        self.intervention.action_demarrer()
        self.assertEqual(self.intervention.state, 'en_cours')

    def test_workflow_termine(self):
        """Test: passage à l'état 'termine' depuis 'en_cours'"""
        self.intervention.action_demarrer()
        self.intervention.write({'rapport': 'Intervention terminée avec succès'})
        self.intervention.action_terminer()
        self.assertEqual(self.intervention.state, 'termine')
