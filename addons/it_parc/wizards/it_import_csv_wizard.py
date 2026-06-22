# -*- coding: utf-8 -*-

import csv
import io
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ItImportCsvWizard(models.TransientModel):
    _name = 'it.import.csv.wizard'
    _description = 'Wizard d\'import CSV d\'équipements'

    @api.model
    def _default_categorie_id(self):
        cat = self.env['it.equipement.categorie'].search([('code', '=', 'PC-LAPTOP')], limit=1)
        if not cat:
            cat = self.env['it.equipement.categorie'].search([], limit=1)
        return cat.id if cat else False

    @api.model
    def _default_site_id(self):
        site = self.env['it.site'].search([('name', 'ilike', 'Abidjan')], limit=1)
        if not site:
            site = self.env['it.site'].search([], limit=1)
        return site.id if site else False

    csv_file = fields.Binary(string='Fichier CSV')
    csv_filename = fields.Char(string='Nom du fichier')
    categorie_id = fields.Many2one('it.equipement.categorie', string='Catégorie par défaut', required=True, default=_default_categorie_id)
    site_id = fields.Many2one('it.site', string='Site par défaut', required=True, default=_default_site_id)
    
    resultat = fields.Text(string='Résultat', readonly=True)
    lignes_crees = fields.Integer(string='Lignes créées', readonly=True)
    lignes_ignores = fields.Integer(string='Lignes ignorées', readonly=True)
    lignes_erreur = fields.Integer(string='Lignes en erreur', readonly=True)

    def action_importer(self):
        """Importer les équipements depuis le CSV"""
        self.ensure_one()
        
        if not self.csv_file:
            raise ValidationError(_('Veuillez sélectionner un fichier CSV.'))
        
        # Décoder le fichier de manière robuste (support utf-8, latin-1, cp1252)
        binary_data = base64.b64decode(self.csv_file)
        try:
            csv_data = binary_data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                csv_data = binary_data.decode('latin-1')
            except UnicodeDecodeError:
                csv_data = binary_data.decode('cp1252', errors='replace')
        
        # Détection du délimiteur (souvent virgule ou point-virgule en français)
        delimiter = ','
        if ';' in csv_data.split('\n')[0]:
            delimiter = ';'
            
        csv_reader = csv.DictReader(io.StringIO(csv_data), delimiter=delimiter)
        
        lignes_crees = 0
        lignes_ignores = 0
        lignes_erreur = 0
        erreurs = []
        
        # Helper pour normaliser les en-têtes
        def normalize_key(key):
            if not key:
                return ''
            k = key.lower().strip()
            # Enlever les slashes, apostrophes et parenthèses
            k = k.replace('/', '').replace("'", "").replace('(', '').replace(')', '')
            # Supprimer accents courants
            for a, b in [('é', 'e'), ('è', 'e'), ('ê', 'e'), ('ë', 'e'), ('à', 'a'), ('ù', 'u'), ('ç', 'c')]:
                k = k.replace(a, b)
            # Remplacer espaces et tirets
            k = k.replace(' ', '_').replace('-', '_')
            while '__' in k:
                k = k.replace('__', '_')
            return k.strip('_')

        # Mappages des en-têtes possibles vers nos champs Odoo
        header_mapping = {
            'name': 'name', 'nom': 'name', 'reference': 'name', 'designation': 'name', 'nom_reference': 'name',
            'numero_serie': 'numero_serie', 'n_serie': 'numero_serie', 'serial': 'numero_serie', 'sn': 'numero_serie', 'num_serie': 'numero_serie', 'numero_de_serie': 'numero_serie',
            'marque': 'marque', 'brand': 'marque',
            'modele': 'modele', 'model': 'modele',
            'processeur': 'processeur', 'cpu': 'processeur',
            'ram': 'ram',
            'disque_dur': 'disque_dur', 'hdd': 'disque_dur', 'ssd': 'disque_dur', 'disque': 'disque_dur',
            'systeme_exploitation': 'systeme_exploitation', 'se': 'systeme_exploitation', 'os': 'systeme_exploitation',
            'adresse_mac': 'adresse_mac', 'mac': 'adresse_mac',
            'adresse_ip': 'adresse_ip', 'ip': 'adresse_ip',
            'date_achat': 'date_achat', 'achat': 'date_achat', 'date_dachat': 'date_achat', 'date_d_achat': 'date_achat',
            'prix_achat': 'prix_achat', 'prix': 'prix_achat', 'cout': 'prix_achat', 'prix_d_achat': 'prix_achat',
            'date_garantie': 'date_garantie', 'garantie': 'date_garantie', 'date_fin_garantie': 'date_garantie', 'date_fin_de_garantie': 'date_garantie',
            'categorie': 'categorie', 'category': 'categorie',
            'site': 'site',
            'etat': 'state', 'state': 'state',
        }

        for row_num, raw_row in enumerate(csv_reader, start=2):  # start=2 car ligne 1 = en-têtes
            try:
                # Normaliser la ligne courante
                row = {}
                for k, v in raw_row.items():
                    norm_k = normalize_key(k)
                    mapped_field = header_mapping.get(norm_k)
                    if mapped_field:
                        row[mapped_field] = v
                
                numero_serie = row.get('numero_serie', '').strip() if row.get('numero_serie') else ''
                if not numero_serie:
                    lignes_erreur += 1
                    erreurs.append(f"Ligne {row_num}: Numéro de série manquant ou en-tête non reconnu")
                    continue
                
                # Vérifier si le numéro de série existe déjà
                existing = self.env['it.equipement'].search([('numero_serie', '=', numero_serie)], limit=1)
                if existing:
                    lignes_ignores += 1
                    erreurs.append(f"Ligne {row_num}: Numéro de série {numero_serie} existe déjà")
                    continue
                
                # Déterminer la catégorie (recherche dynamique)
                cat_name = row.get('categorie', '').strip() if row.get('categorie') else ''
                cat_id = self.categorie_id.id
                if cat_name:
                    cat_record = self.env['it.equipement.categorie'].search([('name', '=ilike', cat_name)], limit=1)
                    if cat_record:
                        cat_id = cat_record.id
                
                # Déterminer le site (recherche dynamique)
                site_name = row.get('site', '').strip() if row.get('site') else ''
                site_id = self.site_id.id
                if site_name:
                    site_record = self.env['it.site'].search([('name', '=ilike', site_name)], limit=1)
                    if site_record:
                        site_id = site_record.id
                
                # Déterminer l'état
                csv_state = row.get('state', '').strip().lower() if row.get('state') else ''
                state = 'brouillon'
                state_mapping = {
                    'brouillon': 'brouillon', 'draft': 'brouillon',
                    'affecte': 'affecte', 'assigned': 'affecte',
                    'maintenance': 'maintenance',
                    'retire': 'retire', 'retired': 'retire'
                }
                if csv_state in state_mapping:
                    state = state_mapping[csv_state]
                elif csv_state:
                    for a, b in [('é', 'e'), ('è', 'e'), ('ê', 'e')]:
                        csv_state = csv_state.replace(a, b)
                    if csv_state in state_mapping:
                        state = state_mapping[csv_state]
                
                # Créer l'équipement
                self.env['it.equipement'].create({
                    'name': row.get('name', '').strip() or numero_serie,
                    'numero_serie': numero_serie,
                    'categorie_id': cat_id,
                    'site_id': site_id,
                    'marque': row.get('marque', ''),
                    'modele': row.get('modele', ''),
                    'processeur': row.get('processeur', ''),
                    'ram': row.get('ram', ''),
                    'disque_dur': row.get('disque_dur', ''),
                    'systeme_exploitation': row.get('systeme_exploitation', ''),
                    'adresse_mac': row.get('adresse_mac', ''),
                    'adresse_ip': row.get('adresse_ip', ''),
                    'date_achat': self._parse_date(row.get('date_achat')),
                    'prix_achat': self._parse_float(row.get('prix_achat')),
                    'date_garantie': self._parse_date(row.get('date_garantie')),
                    'state': state,
                })
                
                lignes_crees += 1
                
            except Exception as e:
                lignes_erreur += 1
                erreurs.append(f"Ligne {row_num}: {str(e)}")
        
        # Générer le rapport
        resultat = f"""Import terminé :
- Lignes créées : {lignes_crees}
- Lignes ignorées (doublons) : {lignes_ignores}
- Lignes en erreur : {lignes_erreur}
"""
        if erreurs:
            resultat += "\nDétails / Erreurs :\n" + "\n".join(erreurs[:20])  # Limiter à 20 erreurs
            if len(erreurs) > 20:
                resultat += f"\n... et {len(erreurs) - 20} autres messages"
        
        self.write({
            'resultat': resultat,
            'lignes_crees': lignes_crees,
            'lignes_ignores': lignes_ignores,
            'lignes_erreur': lignes_erreur,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.import.csv.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _parse_date(self, date_str):
        """Parser une date depuis le CSV de manière robuste"""
        if not date_str:
            return False
        date_str = str(date_str).strip()
        try:
            return fields.Date.from_string(date_str)
        except:
            pass
            
        # Tenter de parser le format DD/MM/YYYY ou DD-MM-YYYY
        for sep in ['/', '-']:
            parts = date_str.split(sep)
            if len(parts) == 3:
                # Si le premier élément est le jour (2 chiffres max) et le dernier l'année (4 chiffres)
                if len(parts[0]) <= 2 and len(parts[2]) == 4:
                    try:
                        return fields.Date.to_date(f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}")
                    except:
                        pass
        return False

    def _parse_float(self, float_str):
        """Parser un flottant depuis le CSV"""
        if not float_str:
            return 0.0
        try:
            return float(str(float_str).replace(',', '.'))
        except:
            return 0.0
