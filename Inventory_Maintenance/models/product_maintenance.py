from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MaintenanceEquipmentLine(models.Model):
    _name = 'maintenance.equipment.line'
    _description = 'Maintenance Equipment Line'
    _rec_name = 'name'
    
    name = fields.Char("Name", required=True)
    product_id = fields.Many2one('product.template', string="Product", required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")
    lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial Number")  # Menambahkan lot_id
    is_important = fields.Boolean("Important")
    type = fields.Selection([
        ('normal', 'Normal'),
        ('sub', 'Sub-Equipment')
    ], string="Type", default='normal')

    @api.constrains('product_id')
    def check_product_id(self):
        for record in self:
            if not record.product_id:
                raise UserError(_("Product is required."))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Cari lot yang terkait dengan product_id
            lot = self.env['stock.production.lot'].search([
                ('product_id', '=', self.product_id.id)
            ], limit=1)  # Mengambil satu lot terkait
            self.lot_id = lot.id if lot else False  # Set lot_id dari produk
