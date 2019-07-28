from odoo import api, fields, models
from datetime import datetime, timedelta

class InTransit(models.Model):
    _name="in.transit"
    # _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'),track_visibility='onchange')
    product_id = fields.Many2one('my.product', 'Product', track_visibility='onchange')
    part_id = fields.Many2one('my.part','Part No.', track_visibility='onchange')
    qty = fields.Float('Qty On Hand', default=1, track_visibility='onchange')
    uom_id = fields.Many2one('my.uom', 'UOM', track_visibility='onchange')








