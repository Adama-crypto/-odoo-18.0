from odoo import models, fields

class EstateRoom(models.Model):
    _name = 'estate.room'
    _description = 'Pièces'

    name = fields.Char(string='Nom', required=True)
    room_type_id = fields.Many2one('estate.room.type', string='Type de pièce', required=True)
    property_id = fields.Many2one('estate.property', string='Propriété', required=True, ondelete='cascade')
    area = fields.Float(string='Superficie')
