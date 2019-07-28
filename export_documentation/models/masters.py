import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp

from odoo.tools import float_compare, pycompat

class MyProduct(models.Model):
    _name = 'my.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    def _compute_oh_hand(self):
        for val in self:
            p = self.env['my.stock'].search([('product_id', '=', val.id), ('uom_id', '=', val.uom_id.id)])
            if p:
                val.on_hand = (p.qty)
            else:
                val.on_hand = 0

    def _compute_in_transit(self):
        for val in self:
            p = self.env['in.transit'].search([('product_id', '=', val.id), ('uom_id', '=', val.uom_id.id)])
            if p:
                val.in_transit = (p.qty)
            else:
                val.in_transit = 0

    name = fields.Char('Name', index=True, required=True, translate=True, track_visibility='onchange',)
    sequence = fields.Integer('Sequence', default=1, track_visibility='onchange',)
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),('stock', 'Stockable'),], string='Product Type', default='stock', required=True, track_visibility='onchange',)
    list_price = fields.Float('Sales Price',digits=(16,4), default=1.0, track_visibility='onchange',)
    standard_price = fields.Float('Cost', track_visibility='onchange',)
    weight = fields.Float('Weight', digits=(16,4), store=True, track_visibility='onchange',)
    license_no = fields.Char('Advance license No.', store=True, track_visibility='onchange',)
    weight_uom_id = fields.Many2one('my.uom', string='Weight UOM', track_visibility='onchange',)
    sale_ok = fields.Boolean('Can be Sold', default=True, track_visibility='onchange',)
    purchase_ok = fields.Boolean('Can be Purchased', default=True, track_visibility='onchange',)
    uom_id = fields.Many2one('my.uom', 'Unit of Measure', required=True, track_visibility='onchange',)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('my.product'), index=1, track_visibility='onchange',)
    active = fields.Boolean('Active', default=True, track_visibility='onchange',)
    image = fields.Binary("Image", attachment=True, track_visibility='onchange',)
    image_medium = fields.Binary("Medium-sized image", attachment=True, track_visibility='onchange',)
    image_small = fields.Binary("Small-sized image", attachment=True, track_visibility='onchange',)
    part_id = fields.Many2one('my.part', string='Part No.',required=True, store=True)
    on_hand = fields.Integer(string='On Hand', compute='_compute_oh_hand',track_visibility='onchange')
    in_transit = fields.Integer(string='In Transit', compute='_compute_in_transit',track_visibility='onchange')
    std_qty_per_pallet = fields.Integer(string='Std Qty Per Pallet')
    tariff = fields.Char(string='Tariff Head', default='8708-9900')

class MyUom(models.Model):
    _name = 'my.uom'

    name = fields.Char('Name')

class MyPart(models.Model):
    _name = 'my.part'

    name = fields.Char('Name')

class MyPaymentTerm(models.Model):
    _name = 'my.payment.term'
    name = fields.Char('Name')

class MyTax(models.Model):
    _name = 'my.tax'
    name = fields.Char('Name')
    amt = fields.Float('Tax(%)')




class MyPartner(models.Model):
    _name = 'my.partner'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Name', index=True, required=True, translate=True, track_visibility='onchange',)
    sequence = fields.Integer('Sequence', default=1, track_visibility='onchange',)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('my.partner'), index=1, track_visibility='onchange',)
    active = fields.Boolean('Active', default=True, track_visibility='onchange',)
    image = fields.Binary("Image", attachment=True, track_visibility='onchange',)
    customer = fields.Boolean('Is a Customer', default=True, track_visibility='onchange',)
    supplier = fields.Boolean('Is a Vendor', default=True, track_visibility='onchange',)

    street = fields.Char('Street', track_visibility='onchange',)
    street2 = fields.Char('Street', track_visibility='onchange',)
    city = fields.Char('City', track_visibility='onchange',)
    state_id = fields.Many2one('res.country.state',string="State")
    zip = fields.Char('Zip', track_visibility='onchange',)
    country_id = fields.Many2one('res.country',string="Country", track_visibility='onchange',)
    vat = fields.Char('GSTIN', track_visibility='onchange',)
    supp_code = fields.Char('Supplier Code', track_visibility='onchange',)
    phone = fields.Char('Phone', track_visibility='onchange',)
    mobile = fields.Char('Mobile', track_visibility='onchange',)
    user_ids = fields.Many2one('res.users',string='Users', track_visibility='onchange',)
    email = fields.Char('Email', track_visibility='onchange',)
    website = fields.Char('Website')
    currency_id = fields.Many2one('res.currency','Currency', track_visibility='onchange',)


