from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    subject_to_maintenance = fields.Boolean(string="Subject to Maintenance")
    equipment_id = fields.Many2one('maintenance.equipment', string="Equipment")
    lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial Number")

    @api.constrains('equipment_id')
    def _check_equipment_count(self):
        for record in self:
            if record.equipment_id:
                count = record.env['maintenance.equipment'].search_count([('product_id', '=', record.id)])
                if count > 1:
                    raise ValidationError("A product can only be associated with one equipment. Please use child equipment for additional units.")

    def action_create_equipment(self):
        self.ensure_one()

        # Check if product already has one equipment
        equipment_count = self.env['maintenance.equipment'].search_count([('product_id', '=', self.id)])
        if equipment_count >= 1:
            raise UserError(_("A product can only be associated with one equipment."))

        if not self.subject_to_maintenance:
            raise UserError(_('Subject to Maintenance must be checked to create equipment.'))

        if self.equipment_id:
            raise UserError(_('Equipment already exists for this product.'))

        # Create the equipment and link it to the product
        equipment = self.env['maintenance.equipment'].create({
            'name': self.name,
            'product_id': self.id,  # Set product_id to the product's ID
            'lot_id': self.lot_id.id if self.lot_id else False  # Set lot_id from the product
        })

        # Link the created equipment to the product
        self.equipment_id = equipment.id
    
    @api.onchange('subject_to_maintenance')
    def _onchange_subject_to_maintenance(self):
        # If the checkbox is checked and tracking is not 'serial', show an error message
        if self.subject_to_maintenance and self.tracking != 'serial':
            self.subject_to_maintenance = False
            raise UserError(_("Maintenance can only be enabled for products with 'By Unique Serial Number'"))

    @api.onchange('tracking')
    def _onchange_tracking(self):
        # Reset lot_id if tracking is not 'serial'
        if self.tracking in ['none', 'lot']:
            self.subject_to_maintenance = False
            self.lot_id = False
        
    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        # If there's only one lot for the product, automatically set lot_id
        if self.lot_id:
            # Automatically fill lot_id if only one lot available
            lots = self.env['stock.production.lot'].search([('product_id', '=', self.id)])
            if len(lots) == 1:
                self.lot_id = lots.id

    @api.constrains('subject_to_maintenance', 'tracking')
    def _check_tracking_for_maintenance(self):
        for record in self:
            if record.subject_to_maintenance and record.tracking != 'serial':
                raise ValidationError("Maintenance can only be enabled for products with 'By Unique Serial Number'")
