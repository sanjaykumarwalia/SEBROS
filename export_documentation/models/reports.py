import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp

from odoo.tools import float_compare, pycompat

class TransactionReports(models.Model):
    _name = 'transaction.reports'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    partner_id = fields.Many2one('my.partner', string='Customer', readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='onchange', )
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    transaction_type = fields.Selection([('Direct', 'Direct'), ('Warehouse', 'Warehouse')], string='Transaction Type',
                                        copy=False, required=True, index=True, track_visibility='onchange',
                                        default='Warehouse')


class StockReports(models.Model):
    _name = 'stock.reports'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')