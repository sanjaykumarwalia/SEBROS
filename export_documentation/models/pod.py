from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError,UserError

class Mypod(models.Model):
    _name="my.pod"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('pod_code')
        vals['name'] = 'POD/19-20/' + str(seq)
        sum_id = super(Mypod, self).create(vals)
        return sum_id

    def _amount_all_wrapper(self):

        for val in self:
            if val.order_line:
                total_amount = 0.00
                for val1 in val.order_line:
                    total_amount = total_amount + val1.price_subtotal
                    val.amount_untaxed = round(total_amount,2)





    def _get_total_amount(self):
        total_amount = 0.00
        for val in self:
            total_amount = val.amount_untaxed
            val.total_amount = round(total_amount,2)
        return True

    @api.depends('payment')
    def _get_due_amount(self):
        due_amount = 0.00
        amt = 0.0
        for val in self:
            if val.payment:
                due_amount = val.total_amount - val.payment
                val.amount_due = round(due_amount,2)
            else:
                val.payment = amt
                val.amount_due = round(val.total_amount,2)
        return True





    @api.multi
    def action_confirm(self):
        if self.order_line:
            for val in self.order_line:
                pod_obj = self.env['my.stock'].search([('product_id', '=', val.product_id.id),('part_id', '=', val.product_id.part_id.id),('uom_id', '=', val.uom_id.id)])

                if pod_obj.qty>=val.qty:
                    pod_obj.write({'qty': pod_obj.qty - val.qty})
                else:
                    raise UserError(("%s Not In Stock"%(val.product_id.name)))
                self.write({'state': 'done'})
        return True

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True

    name = fields.Char(string='POD No.', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: ('New'),track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
        ('done', 'Locked'),

    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')



    date = fields.Datetime(string='Date', required=True, readonly=True, index=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now, track_visibility='onchange',)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('my.partner', string='Customer', readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='onchange',)
    payment_term_id = fields.Many2one('my.payment.term', string='Payment Terms', track_visibility='onchange')
    order_line = fields.One2many('my.pod.line', 'order_id', string='Order Lines',
                                 states={'done': [('readonly', True)]}, copy=True,
                                 auto_join=True, track_visibility='onchange',)
    amount_untaxed = fields.Float(compute=_amount_all_wrapper, string='Untaxed Amount',track_visibility='onchange')
    total_amount = fields.Float(compute=_get_total_amount, string='Total Amount',track_visibility='onchange')
    payments_widget = fields.Text(compute='_get_payment_info_JSON', groups="account.group_account_invoice")
    amount_due = fields.Float(compute=_get_due_amount, string='Amount Due',track_visibility='onchange')
    reference = fields.Char('Reference.', track_visibility='onchange',)

    payment = fields.Float(string='Paid Amount',track_visibility='onchange')




class MypodLine(models.Model):
    _name = "my.pod.line"

    def get_subtotal(self):
        total_price = 0.00
        for val in self:
            if val.qty:
                total_price = (val.qty * val.unit_price)
                val.write({'price_subtotal1':total_price})
                val.price_subtotal = round(total_price,2)

    @api.onchange('product_id')
    def onchange_product_id(self):
        unit_price = 0.0
        rate = 0.0
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.unit_price = self.product_id.list_price
            self.part_id = self.product_id.part_id.id
            self.name = self.product_id.name

    order_id = fields.Many2one('my.pod','Id',track_visibility='onchange')
    product_id = fields.Many2one('my.product','Product',track_visibility='onchange')
    part_id = fields.Many2one('my.part','Part No.', track_visibility='onchange')
    date = fields.Date('Date')
    uom_id = fields.Many2one('my.uom','UOM',track_visibility='onchange')
    qty = fields.Float('Qty', default=1,track_visibility='onchange')
    unit_price = fields.Float('Unit Price',digits=(16,4),track_visibility='onchange')
    price_subtotal = fields.Float(compute = get_subtotal, string='Subtotal',track_visibility='onchange')
    price_subtotal1 = fields.Float(string='Subtotal',track_visibility='onchange')





