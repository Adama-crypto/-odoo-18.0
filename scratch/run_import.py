# -*- coding: utf-8 -*-
import base64
import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import odoo
import odoo.modules.registry as registry
import odoo.tools.config as config

# Configuration Odoo
config.parse_config(['-c', 'odoo.conf'])

# Déterminer le fichier CSV de l'utilisateur
# On cherche "Équipement Informatique (it.equipement).csv" dans les Téléchargements
csv_path = r"c:\Users\MSI\Downloads\Équipement Informatique (it.equipement).csv"

if not os.path.exists(csv_path):
    # Essayer sans accent si problème de système de fichiers
    csv_path = r"c:\Users\MSI\Downloads\Equipement Informatique (it.equipement).csv"
    if not os.path.exists(csv_path):
        print(f"ERREUR: Fichier CSV introuvable !")
        sys.exit(1)

print(f"Fichier CSV trouvé à: {csv_path}")

reg = registry.Registry.new('test_it_parc')
with reg.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    
    print("Lecture et encodage du fichier CSV...")
    with open(csv_path, 'rb') as f:
        csv_binary = base64.b64encode(f.read())
    
    # Trouver une catégorie et un site
    categorie = env['it.equipement.categorie'].search([], limit=1)
    site = env['it.site'].search([], limit=1)

    # Supprimer l'équipement SN123456789 pour forcer la création et tester la ligne
    existing_test = env['it.equipement'].search([('numero_serie', '=', 'SN123456789')])
    if existing_test:
        print("Suppression de l'équipement SN123456789 existant pour le test...")
        existing_test.unlink()
    
    if not categorie:
        categorie = env['it.equipement.categorie'].create({'name': 'PC Portable', 'code': 'PC-LAPTOP'})
    if not site:
        site = env['it.site'].create({'name': 'Abidjan - Siège'})
        
    print(f"Catégorie par défaut: {categorie.name} (ID: {categorie.id})")
    print(f"Site par défaut: {site.name} (ID: {site.id})")
    
    # Créer le wizard
    wizard = env['it.import.csv.wizard'].create({
        'csv_file': csv_binary,
        'csv_filename': os.path.basename(csv_path),
        'categorie_id': categorie.id,
        'site_id': site.id,
    })
    
    print("Lancement de action_importer()...")
    try:
        wizard.action_importer()
        print("Importation terminée.")
        print(f"LOGS DU WIZARD :\n{wizard.resultat}")
        print(f"Créés: {wizard.lignes_crees} | Ignorés: {wizard.lignes_ignores} | Erreurs: {wizard.lignes_erreur}")
        
        # Vérifier l'enregistrement créé
        equip = env['it.equipement'].search([('numero_serie', '=', 'SN123456789')], limit=1)
        if equip:
            print("--- VÉRIFICATION DE L'ÉQUIPEMENT CRÉÉ ---")
            print(f"Nom / Référence : {equip.name}")
            print(f"Numéro de série : {equip.numero_serie}")
            print(f"Catégorie       : {equip.categorie_id.name} (Code: {equip.categorie_id.code})")
            print(f"Site            : {equip.site_id.name}")
            print(f"Date de garantie: {equip.date_garantie}")
            print(f"État            : {equip.state}")
            print("-----------------------------------------")
        else:
            print("ERREUR: L'équipement créé est introuvable !")
            
        # Valider pour voir si tout s'insère bien en base de données
        cr.commit()
        print("Base de données mise à jour avec succès !")
    except Exception as e:
        cr.rollback()
        print(f"ERREUR LORS DE L'IMPORTATION: {str(e)}")
        import traceback
        traceback.print_exc()
