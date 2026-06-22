# Odoo 18 - TECHPARK CI

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Odoo](https://img.shields.io/badge/Odoo-18.0-875A7B.svg)](https://www.odoo.com/)
[![License](https://img.shields.io/badge/License-LGPL--3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Build Status](https://runbot.odoo.com/runbot/badge/flat/1/master.svg)](https://runbot.odoo.com/runbot)

> 🇨🇮 Déploiement Odoo 18 personnalisé pour **TECHPARK CI** — incluant des modules métier sur mesure pour la gestion du parc informatique et la gestion de boutique.

---

## 📦 Modules personnalisés

### 🖥️ `it_parc` — Gestion du Parc Informatique
Module complet de gestion du parc informatique d'entreprise :
- Suivi des équipements (PC, serveurs, imprimantes, réseau, téléphones IP)
- Affectation aux employés avec historique
- Interventions de maintenance (curative, préventive, upgrade)
- Contrats fournisseurs avec alertes d'expiration
- Import CSV en masse
- Rapports PDF et exports Excel
- Dashboard DSI (OWL 2) avec KPIs et graphiques

### 🛒 `shop_manager` — Gestion de Boutique
Module de gestion des ventes et produits en boutique.

### 🏠 `estate` — Gestion Immobilière
Module de gestion des biens immobiliers.

---

## 🚀 Démarrage rapide

### Prérequis
- Python 3.11+
- PostgreSQL 13+
- Odoo 18

### Lancement

```bash
# Se placer dans le dossier du projet
cd odoo-18.0

# Lancer Odoo avec le module it_parc
python odoo-bin -c odoo.conf -d ma_base -u it_parc

# Lancer avec mise à jour de tous les modules personnalisés
python odoo-bin -c odoo.conf -d ma_base -u it_parc,shop_manager,estate
```

### Configuration `odoo.conf`
```ini
[options]
db_host = localhost
db_port = 5432
db_user = odoo
db_password = votre_mot_de_passe
addons_path = addons
```

---

## 🧪 Tests

Pour lancer les tests unitaires du module `it_parc` :

```bash
python odoo-bin -c odoo.conf -d test_db --test-enable -u it_parc --stop-after-init
```

Les tests couvrent :
- `test_it_equipement.py` — Création, numéro de série unique, calcul d'âge et garantie
- `test_it_contrat.py` — Création, jours restants, contrats expirés
- `test_it_intervention.py` — Création, durée calculée, transitions de workflow

---

## 📁 Structure du projet

```
odoo-18.0/
├── addons/
│   ├── it_parc/          # Module Parc Informatique (TECHPARK CI)
│   ├── shop_manager/     # Module Gestion Boutique
│   └── estate/           # Module Immobilier
├── odoo/                 # Core Odoo 18
├── odoo-bin              # Point d'entrée Odoo
└── odoo.conf             # Configuration
```

---

## 👨‍💻 Auteur

**TECHPARK CI** — 2024-2025

---

## 📄 Licence

Ce projet est basé sur Odoo 18 distribué sous licence [LGPL-3](LICENSE).
Les modules personnalisés (`it_parc`, `shop_manager`, `estate`) sont développés par TECHPARK CI.
