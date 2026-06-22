from odoo import models, fields

class EstateRoomType(models.Model):
    _name = 'estate.room.type'
    _description = 'Types de pièces'

    name = fields.Char(string='Libellé', required=True)
    description = fields.Text(string='Description')
    room_ids = fields.One2many('estate.room', 'room_type_id', string='Liste des pièces liées à ce type')
