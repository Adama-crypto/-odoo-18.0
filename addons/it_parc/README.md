# IT Parc - Module de Gestion du Parc Informatique

Module Odoo 18 Enterprise pour la gestion complète du parc informatique de TECHPARK CI.

## Description

Ce module permet de gérer l'ensemble des équipements informatiques (PCs, serveurs, imprimantes, réseau, téléphones IP) avec traçabilité complète des affectations, interventions de maintenance, contrats fournisseurs et alertes automatiques.

## Fonctionnalités

### 1. Gestion des équipements
- Workflow à 4 états : Brouillon → Affecté → En maintenance → Retiré
- Numéro de série unique
- Caractéristiques techniques (processeur, RAM, disque dur, OS, adresses MAC/IP)
- Informations financières (date d'achat, prix, garantie)
- Calcul automatique de l'âge et des jours de garantie restants

### 2. Affectation aux employés
- Lien avec le module HR d'Odoo
- Historique complet de toutes les affectations
- Wizard de réaffectation avec saisie du motif obligatoire
- Gestion des sites et départements

### 3. Suivi des interventions
- Technicien, dates début/fin, durée calculée automatiquement
- Coût, rapport d'intervention, pièces remplacées
- Vue calendrier des interventions planifiées
- États : Planifiée, En cours, Terminée, Annulée

### 4. Contrats fournisseurs
- Maintenance et licences
- Période de validité, montant
- Équipements couverts
- Jours restants calculés dynamiquement
- Wizard de renouvellement

### 5. Alertes automatiques
- Configuration des délais d'alerte
- Deux modes : scan manuel via wizard + déclenchement automatique par tâche planifiée
- Alertes sur garanties et contrats

### 6. Import CSV en masse
- Wizard d'import
- Création des équipements manquants
- Détection des doublons par numéro de série
- Rapport d'import (lignes créées / ignorées / en erreur)

### 7. Rapports PDF (QWeb)
- Fiche individuelle d'équipement
- Inventaire complet filtrable par département ou catégorie
- Historique des maintenances par période avec coût total

### 8. Exports Excel (xlsxwriter)
- Inventaire complet (toutes colonnes)
- Synthèse des coûts de maintenance par équipement et par mois
- Contrats expirant dans les 60 jours avec mise en couleur conditionnelle

### 9. Dashboard DSI (OWL 2)
- 4 KPIs : Total équipements, Équipements affectés, En maintenance, Interventions en cours
- Graphique : Équipements par catégorie
- Graphique : Interventions par mois

## Installation

### Prérequis
- Odoo 18 Enterprise
- Python 3.11+
- Dépendances Odoo : hr, stock, purchase, account, maintenance, mail, contacts, web

### Étapes d'installation
1. Copier le dossier `it_parc` dans le répertoire `addons` d'Odoo
2. Redémarrer Odoo
3. Aller dans Apps → Mettre à jour la liste des applications
4. Rechercher "IT Parc"
5. Installer le module

## Configuration

### Groupes d'utilisateurs
- **IT Technicien** : Lecture + création d'interventions uniquement
- **IT Manager** : Accès complet à tout le module

### Sites par défaut
- Abidjan - Siège
- Abidjan - Annexe
- Bouaké

### Catégories d'équipement par défaut
- PC Portable
- PC Fixe
- Serveur
- Imprimante
- Équipement réseau
- Téléphone IP

### Alertes par défaut
- Alerte Garantie : 30 jours avant expiration
- Alerte Contrat : 60 jours avant expiration

## Utilisation

### Créer un équipement
1. Aller dans IT Parc → Équipements → Tous les équipements
2. Cliquer sur "Créer"
3. Remplir les informations obligatoires (nom, numéro de série, catégorie, site)
4. Sauvegarder

### Affecter un équipement
1. Ouvrir l'équipement
2. Cliquer sur le bouton "Affecter"
3. Sélectionner l'employé et la date de début
4. Confirmer

### Créer une intervention
1. Aller dans IT Parc → Interventions
2. Cliquer sur "Créer"
3. Sélectionner l'équipement, le technicien, le type et la priorité
4. Décrire le problème
5. Sauvegarder

### Importer des équipements depuis CSV
1. Aller dans IT Parc → Importer CSV
2. Sélectionner le fichier CSV
3. Choisir la catégorie et le site par défaut
4. Cliquer sur "Importer"

### Générer des rapports
- **Fiche équipement** : Ouvrir l'équipement → Action → Imprimer → Fiche équipement
- **Inventaire** : IT Parc → Équipements → Action → Imprimer → Inventaire
- **Maintenance** : IT Parc → Interventions → Action → Imprimer → Historique maintenances

### Exporter vers Excel
- **Inventaire** : IT Parc → Équipements → Action → Exporter inventaire Excel
- **Coûts maintenance** : IT Parc → Interventions → Action → Exporter coûts maintenance Excel
- **Contrats expirants** : IT Parc → Contrats → Action → Exporter contrats expirants Excel

### Accéder au Dashboard
- Aller dans IT Parc → Dashboard

## Structure du module

```
it_parc/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── it_equipement.py
│   ├── it_affectation.py
│   ├── it_intervention.py
│   ├── it_contrat.py
│   ├── it_alerte.py
│   └── it_export_excel.py
├── views/
│   ├── it_equipement_views.xml
│   ├── it_affectation_views.xml
│   ├── it_intervention_views.xml
│   ├── it_contrat_views.xml
│   ├── it_alerte_views.xml
│   ├── it_parc_menu.xml
│   └── it_dashboard_views.xml
├── wizards/
│   ├── __init__.py
│   ├── it_reaffectation_wizard.py
│   ├── it_reaffectation_wizard_views.xml
│   ├── it_renouvellement_contrat_wizard.py
│   ├── it_renouvellement_contrat_wizard_views.xml
│   ├── it_import_csv_wizard.py
│   ├── it_import_csv_wizard_views.xml
│   ├── it_scan_alertes_wizard.py
│   └── it_scan_alertes_wizard_views.xml
├── report/
│   ├── it_equipement_report.xml
│   ├── it_inventaire_report.xml
│   └── it_maintenance_report.xml
├── security/
│   ├── ir.model.access.csv
│   └── it_parc_security.xml
├── data/
│   ├── it_parc_data.xml
│   ├── ir_cron.xml
│   └── it_parc_demo.xml
├── controllers/
│   ├── __init__.py
│   └── main.py
├── static/
│   └── src/
│       └── dashboard/
│           ├── dashboard.js
│           ├── dashboard.xml
│           └── dashboard.scss
└── README.md
```

## Données de démo

Le module inclut des données de démo :
- 10 équipements (PCs, serveurs, imprimantes, réseau, téléphones)
- 3 contrats (maintenance, licence, support)
- 5 interventions (curatives, préventives, upgrade)

## Tâche planifiée

Une tâche planifiée (`ir.cron`) est configurée pour scanner automatiquement les alertes quotidiennement.

## Support

Pour toute question ou problème, contactez l'équipe technique de TECHPARK CI.

## Licence

LGPL-3

## Auteur

TECHPARK CI - 2024
