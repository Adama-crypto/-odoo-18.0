# -*- coding: utf-8 -*-
import base64
import os
import sys

# Charger l'environnement Odoo si lancé en shell
# Ce script doit être exécuté avec: python odoo-bin -c odoo.conf -d test_it_parc shell < scratch/test_import_csv.py

csv_path = r"c:\Users\MSI\Downloads\Équipement Informatique (it.equipement).csv"

if not os.path.exists(csv_path):
    print(f"ERREUR: Le fichier CSV n'existe pas à l'emplacement: {csv_path}")
    sys.exit(1)

print(f"Lecture du fichier CSV: {csv_path}...")
with open(csv_path, 'rb') as f:
    csv_binary = base64.b64encode(f.read())

# Trouver une catégorie et un site existants pour l'import
categorie = env['it.equipement.categorie'].search([], limit=1)
site = env['it.site'].search([], limit=1)

if not categorie or not site:
    print("ERREUR: Catégorie ou site inexistant en BD. Création par défaut...")
    if not categorie:
        categorie = env['it.equipement.categorie'].create({'name': 'PC Portable', 'code': 'PC-LAPTOP'})
    if not site:
        site = env['it.site'].create({'name': 'Abidjan - Siège'})

print(f"Utilisation de la catégorie: {categorie.name} (ID: {categorie.id})")
print(f"Utilisation du site: {site.name} (ID: {site.id})")

# Créer le wizard d'importation
wizard = env['it.import.csv.wizard'].create({
    'csv_file': csv_binary,
    'csv_filename': 'Équipement Informatique (it.equipement).csv',
    'categorie_id': categorie.id,
    'site_id': site.id,
})

print("Exécution de l'importation...")
try:
    action = wizard.action_importer()
    print("Action d'importation exécutée avec succès !")
    # Recharger le wizard pour lire le résultat
    wizard.invalidate_model_cache()
    print(f"RÉSULTAT DE L'IMPORTATION :\n{wizard.resultat}")
    print(f"Lignes créées: {wizard.lignes_crees}")
    print(f"Lignes ignorées: {wizard.lignes_ignores}")
    print(f"Lignes erreur: {wizard.lignes_erreur}")
except Exception as e:
    print(f"ERREUR CRITIQUE lors de l'exécution de action_importer: {str(e)}")
    import traceback
    traceback.print_exc()

# Annuler la transaction pour ne pas modifier la BD de test de façon permanente si on veut juste tester
# env.cr.rollback()
# print("Transaction annulée.")
