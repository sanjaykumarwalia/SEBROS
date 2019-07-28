import PyPDF2
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero, float_compare, pycompat
from reportlab.pdfgen import canvas
import webbrowser
from num2words import num2words
import base64
from datetime import datetime
from odoo.exceptions import UserError, ValidationError



class InvoicePayment(models.Model):
    _name = "invoice.payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('invoice_payment')
        vals['name'] = 'Pay' + str(seq)
        sum_id = super(InvoicePayment, self).create(vals)
        return sum_id


    def action_fetch_data(self):
        if not self.payment_history_line:
            invoice_obj = self.env['my.invoice'].search([('partner_id','=',self.partner_id.id),('due_amount1','>', 0.00),('state','=','done'),('transaction_type','=','Direct')],order = "name asc")
            pod_obj = self.env['my.pod'].search([('partner_id','=',self.partner_id.id),('amount_due','>', 0.00),('state','=','done')])
            if invoice_obj:
                for val in invoice_obj:

                    self.env['payment.history.line'].create({'payment_id': self.id, 'invoice_id': val.id,'gtotal':val.total_amount,
                                                             'amount_due':val.due_amount,
                                                              'payment_date': datetime.today(),
                                                               })

            if pod_obj:
                for val1 in pod_obj:
                    if val1.amount_due > 0:
                        self.env['payment.history.line'].create({'payment_id': self.id, 'pod_id': val1.id,'gtotal':val1.total_amount,
                                                             'amount_due':val1.amount_due,
                                                              'payment_date': datetime.today(),
                                                               })

    def action_confirm(self):
        if self.amount_due == 0.00 and self.invoice_amount != 0.00 :

            if self.payment_history_line:
                for val in self.payment_history_line:
                    if val.invoice_id:
                        invoice_obj = self.env['my.invoice'].search([('id', '=', val.invoice_id.id)])
                        invoice_obj.write({'payment':invoice_obj.payment + val.amount})
                    if val.pod_id:
                        pod_obj = self.env['my.pod'].search([('id', '=', val.pod_id.id)])
                        pod_obj.write({'payment':pod_obj.payment + val.amount})
                self.write({'state':'confirm'})

        else:
            raise UserError(_('Difference Must be Zero Or Receive Amount Can Not Be Zero.'))




    def _get_due_amount(self):
        due_amount = 0.00

        for val in self:
            if val.payment_history_line:
                amt = 0.0
                for val1 in val.payment_history_line:
                    amt = amt + val1.amount
                due_amount = val.invoice_amount - amt - val.sort_value
                val.amount_due = due_amount
            else:
                val.amount_due = val.invoice_amount
        return True

    @api.one
    @api.depends('payment_history_line.amount')
    def _amount_all_wrapper(self):

        for val in self:
            if val.payment_history_line:
                total_amount = 0.00
                for val1 in val.payment_history_line:
                    total_amount = total_amount + val1.amount
                    val.paid_amount = total_amount

    name = fields.Char(string='No.', copy=False, readonly=True, track_visibility='onchange')

    date = fields.Datetime(string='Date', required=True, readonly=True, index=True, default=fields.Datetime.now)

    partner_id = fields.Many2one('my.partner',string='Customer', track_visibility='always')

    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)

    invoice_amount = fields.Float('Receive Amount', track_visibility='onchange')
    paid_amount = fields.Float(compute=_amount_all_wrapper, string='Paid Amount', track_visibility='onchange')
    sort_value = fields.Float('Sort Value')

    amount_due = fields.Float(compute=_get_due_amount, string='Difference', track_visibility='onchange')

    payment_history_line = fields.One2many('payment.history.line', 'payment_id', "Payment Line",
                                           track_visibility='onchange')

    payment_ref = fields.Char('Payment Reference')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),

    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')




class PaymentHistoryLine(models.Model):
    _name = "payment.history.line"


    @api.multi
    def write(self, vals):
        sum_id = super(PaymentHistoryLine, self).write(vals)
        if self.amount == 0.0:
            self.unlink()

        return sum_id



    @api.onchange('amount_due','select')
    def onchange_select(self):
        if self.select:
            self.amount = self.amount_due
        else:
            self.amount = 0.0

    select = fields.Boolean('Select',  default= True)
    payment_id = fields.Many2one('invoice.payment', 'Id')
    invoice_id = fields.Many2one('my.invoice', 'Invoice No.', track_visibility='onchange')
    pod_id = fields.Many2one('my.pod','POD', track_visibility='onchange')
    payment_date = fields.Date('Payment Date')
    gtotal = fields.Float('GTotal')
    amount_due = fields.Float('Due Amount')
    amount = fields.Float('Amount')
    payment_type = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], default='bank', string="Payment Type")








