from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class MaintenanceEquipmentInherit(models.Model):
    _inherit = 'maintenance.equipment'

    product_id = fields.Many2one('product.product', string="Product")
    lot_id = fields.Many2one('stock.lot', string="Lot/Serial Number", domain="[('product_id', '=', product_id)]")  # Relasi ke stock.lot
    serial_no = fields.Char(string="Serial Number")  # Ensure serial_no is retained
    sub_equipment_ids = fields.Many2many("maintenance.equipment", "sub_equipment_equipment_rel", "maintenance_equipment_id", "sub_equipment_id", string="Sub Equipment")
    all_sub_equipment_ids = fields.Many2many("maintenance.equipment", "all_sub_equipment_equipment_rel", "maintenance_equipment_id", "all_sub_equipment_id", string="All Equipment")

    def get_all_subequipment(self, data, equipment_id):
        data.append(equipment_id._origin.id)
        if not equipment_id.sub_equipment_ids:
            return data
        for line in equipment_id.sub_equipment_ids:
            data.append(line._origin.id)
            if line.sub_equipment_ids:
                data = self.get_all_subequipment(data,line)
        return data
            

    @api.onchange("sub_equipment_ids")
    def onchange_sub_equipment(self):
        # GET ALL SUB EQUIPMENT
        data = []
        for s_equipment_line in self.sub_equipment_ids:
            data = self.get_all_subequipment(data, s_equipment_line)
        self.all_sub_equipment_ids = [(6,0,data)]


    @api.depends('lot_id', 'product_id')
    def _compute_serial_no(self):
        for record in self:
            if record.lot_id and record.product_id:
                # Format serial_no as per product name and lot number
                product_prefix = (record.product_id.name or '').replace(' ', '').upper()[:3]  # First 3 letters of the product name
                lot_number = record.lot_id.name or ''
                record.serial_no = f"{product_prefix}{lot_number}"

    @api.model
    def default_get(self, fields_list):
        res = super(MaintenanceEquipmentInherit, self).default_get(fields_list)
        
        if 'product_id' in fields_list and self._context.get('default_product_id'):
            product_id = self._context.get('default_product_id')
            product_tmpl_id = self.env['product.template'].browse(product_id)
            product_id = product_tmpl_id.product_variant_id
            res.update({
                'product_id': product_id.id,
                'lot_id': self._get_lot_from_product(product_id.id)
            })
        return res


    def _get_lot_from_product(self, product_id):
        """Dapatkan lot (stock.lot) berdasarkan product_id"""
        lot = self.env['stock.lot'].search([('product_id', '=', product_id)], limit=1)
        return lot.id if lot else False

    @api.depends('name', 'serial_no')
    def _compute_display_name(self):
        for record in self:
            name = record.name or ''
            serial_no = record.serial_no or ''
            record.display_name = f"{name}"

    @api.model
    def create(self, vals):
        product_id = vals.get('product_id')
        lot_id = vals.get('lot_id')
        if lot_id:
            lot = self.env['stock.lot'].browse(lot_id)
            product = self.env['product.product'].browse(product_id)
            # Format serial_no as per product name and lot number
            product_prefix = (product.name or '').replace(' ', '').upper()[:3]
            vals['serial_no'] = f"{product_prefix}{lot.name}"

        # If product_id is in context, set lot_id and product_id
        if product_id:
            product = self.env['product.product'].browse(product_id)
            vals['product_id'] = product.id
            vals['lot_id'] = self._get_lot_from_product(product_id)

            # Check tracking type
            if product.tracking != 'serial':
                existing_equipment = self.env['maintenance.equipment'].search([
                    ('product_id', '=', product_id)
                ])
                if existing_equipment:
                    raise ValidationError(_("This product already has an equipment and cannot have more than one if tracking is not 'By Unique Serial Number'."))

        return super(MaintenanceEquipmentInherit, self).create(vals)

    def write(self, vals):
        if 'lot_id' in vals:
            lot = self.env['stock.lot'].browse(vals['lot_id'])
            product = self.env['product.product'].browse(vals.get('product_id'))
            # Format serial_no as per product name and lot number
            product_prefix = (product.name or '').replace(' ', '').upper()[:3]
            vals['serial_no'] = f"{product_prefix}{lot.name}"

        if 'product_id' in vals:
            product_id = vals.get('product_id')
            product = self.env['product.product'].browse(product_id)
            if product.tracking != 'serial':
                existing_equipment = self.env['maintenance.equipment'].search([
                    ('product_id', '=', product_id)
                ])
                if len(existing_equipment) > 1:
                    raise ValidationError("This product already has an equipment and cannot have more than one if tracking is not 'By Unique Serial Number'.")

        return super(MaintenanceEquipmentInherit, self).write(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            lot = self.env['stock.lot'].search([
                ('product_id', '=', self.product_id.id)
            ], limit=1)  # Select one lot associated with the product
            self.lot_id = lot.id if lot else False


