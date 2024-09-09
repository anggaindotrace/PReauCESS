from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    equipment_id = fields.Many2one('maintenance.equipment.line', string="Equipment")
