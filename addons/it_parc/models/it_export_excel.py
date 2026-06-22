# -*- coding: utf-8 -*-

import xlsxwriter
from io import BytesIO
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64


class ItEquipement(models.Model):
    _inherit = 'it.equipement'

    def action_export_inventaire_excel(self):
        """Export de l'inventaire complet en Excel"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Inventaire')
        
        # Styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
        })
        
        # Headers
        headers = [
            'Nom', 'Numéro de série', 'Catégorie', 'Marque', 'Modèle',
            'Processeur', 'RAM', 'Disque dur', 'OS', 'Adresse MAC', 'Adresse IP',
            'Site', 'Département', 'Employé', 'État', 'Date achat', 'Prix achat',
            'Date garantie', 'Jours garantie restants', 'Nombre interventions', 'Coût total maintenance'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 20)
        
        # Data
        equipments = self.search([])
        for row, equip in enumerate(equipments, start=1):
            data = [
                equip.name or '',
                equip.numero_serie or '',
                equip.categorie_id.name or '',
                equip.marque or '',
                equip.modele or '',
                equip.processeur or '',
                equip.ram or '',
                equip.disque_dur or '',
                equip.systeme_exploitation or '',
                equip.adresse_mac or '',
                equip.adresse_ip or '',
                equip.site_id.name or '',
                equip.departement_id.name or '',
                equip.employe_id.name or '',
                dict(equip._fields['state'].selection).get(equip.state, ''),
                str(equip.date_achat) if equip.date_achat else '',
                equip.prix_achat or 0,
                str(equip.date_garantie) if equip.date_garantie else '',
                equip.jours_garantie_restants or 0,
                equip.nombre_interventions or 0,
                equip.cout_total_maintenance or 0,
            ]
            
            for col, value in enumerate(data):
                worksheet.write(row, col, value, cell_format)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'inventaire_{fields.Date.today()}.xlsx',
            'datas': base64.b64encode(output.read()),
            'res_model': 'it.equipement',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
        }


class ItIntervention(models.Model):
    _inherit = 'it.intervention'

    def action_export_couts_maintenance_excel(self):
        """Export des coûts de maintenance par équipement et par mois"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Coûts Maintenance')
        
        # Styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '#,##0',
        })
        
        # Headers
        headers = [
            'Équipement', 'Numéro de série', 'Référence intervention',
            'Technicien', 'Type', 'Date début', 'Date fin', 'Durée (h)', 'Coût (FCFA)'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 20)
        
        # Data
        interventions = self.search([('state', '=', 'termine')])
        for row, intervention in enumerate(interventions, start=1):
            data = [
                intervention.equipement_id.name or '',
                intervention.equipement_id.numero_serie or '',
                intervention.name or '',
                intervention.technicien_id.name or '',
                dict(intervention._fields['type_intervention'].selection).get(intervention.type_intervention, ''),
                str(intervention.date_debut) if intervention.date_debut else '',
                str(intervention.date_fin) if intervention.date_fin else '',
                intervention.duree_heures or 0,
                intervention.cout or 0,
            ]
            
            for col, value in enumerate(data):
                if col == 8:  # Coût column
                    worksheet.write(row, col, value, number_format)
                else:
                    worksheet.write(row, col, value, cell_format)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'couts_maintenance_{fields.Date.today()}.xlsx',
            'datas': base64.b64encode(output.read()),
            'res_model': 'it.intervention',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
        }


class ItContrat(models.Model):
    _inherit = 'it.contrat'

    def action_export_contrats_expirants_excel(self):
        """Export des contrats expirant dans les 60 jours avec mise en couleur"""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Contrats Expirants')
        
        # Styles
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
        })
        
        alert_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': '#FFC7CE',
        })
        
        warning_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': '#FFEB9C',
        })
        
        # Headers
        headers = [
            'Référence', 'Fournisseur', 'Type', 'Date début', 'Date fin',
            'Durée (jours)', 'Montant (FCFA)', 'Jours restants', 'État'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, 20)
        
        # Data - contrats expirant dans 60 jours
        from datetime import timedelta
        date_limite = fields.Date.today() + timedelta(days=60)
        contrats = self.search([
            ('date_fin', '>=', fields.Date.today()),
            ('date_fin', '<=', date_limite),
            ('state', '=', 'actif'),
        ])
        
        for row, contrat in enumerate(contrats, start=1):
            # Choose format based on days remaining
            if contrat.jours_restants <= 15:
                fmt = alert_format
            elif contrat.jours_restants <= 30:
                fmt = warning_format
            else:
                fmt = cell_format
            
            data = [
                contrat.name or '',
                contrat.fournisseur_id.name or '',
                dict(contrat._fields['type_contrat'].selection).get(contrat.type_contrat, ''),
                str(contrat.date_debut) if contrat.date_debut else '',
                str(contrat.date_fin) if contrat.date_fin else '',
                contrat.duree_jours or 0,
                contrat.montant or 0,
                contrat.jours_restants or 0,
                dict(contrat._fields['state'].selection).get(contrat.state, ''),
            ]
            
            for col, value in enumerate(data):
                worksheet.write(row, col, value, fmt)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'contrats_expirants_{fields.Date.today()}.xlsx',
            'datas': base64.b64encode(output.read()),
            'res_model': 'it.contrat',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
        }
