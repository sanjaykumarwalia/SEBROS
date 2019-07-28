from odoo import api, fields, models
from datetime import datetime, timedelta


class MySale(models.Model):
    _name="my.sale"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('sale_code')
        vals['name'] = 'SO' + str(seq)
        sum_id = super(MySale, self).create(vals)
        return sum_id

    def _amount_all_wrapper(self):
        total_amount = 0.00
        for val in self:
            if val.order_line:
                for val1 in val.order_line:
                    total_amount = total_amount + val1.price_subtotal
                    self.amount_untaxed = total_amount

    def _tax_amount(self):
        total_tax = 0.00
        for val in self:
            if val.order_line:
                for val1 in val.order_line:
                    amount = 0.0
                    if val1.tax_id:
                        for val2 in val1.tax_id:
                            amount = amount + val2.amt
                    else:
                        amount = val1.tax_id.amt
                    total_tax = total_tax + (val1.qty * val1.unit_price)* amount / 100
                    self.tax_value = total_tax

    def _get_total_amount(self):
        total_amount = 0.00
        for val in self:
            total_amount = val.amount_untaxed + val.tax_value
            self.total_amount = total_amount

    def _compute_ordered_qty(self):
        total_qty = 0.00
        for val in self:
            if val.order_line:
                for val1 in val.order_line:
                    if val1.product_id and val1.qty:
                        total_qty = total_qty + val1.qty
            val.ordered_qty = total_qty

    def _compute_exported_qty(self):
        total_qty = 0.00
        for val in self:
            if val.order_line:
                for val1 in val.order_line:
                    if val1.product_id and val1.export_qty:
                        total_qty = total_qty + val1.export_qty
            val.exported_qty = total_qty

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_export_invoice(self):
        view = self.env.ref('export_documentation.view_sale_wizard')
        if self.ordered_qty <= self.exported_qty:
            self.write({'state': 'done'})
        else:
            return {
                'name': ('Sale Wizard'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': self.env.context,
            }

    @api.depends('transaction_ids')
    def _compute_export_ids(self):
        for order in self:
            order.invoice_count = len(order.transaction_ids)




    name = fields.Char(string='Sale No.', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: ('New'),track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Runing'),
        ('cancel', 'Cancel'),
        ('done', 'Locked'),

    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    po_type = fields.Selection([('close', 'Close'),('open', 'Open')], string='PO Type', track_visibility='onchange', default='close')
    date = fields.Date(string='Date', required=True, readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Date.today)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('my.partner', string='Customer', readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='always')
    ship_to = fields.Many2one('my.partner', string='Ship To ', readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='always')
    payment_term_id = fields.Many2one('my.payment.term', string='Payment Terms', track_visibility='onchange')

    order_line = fields.One2many('my.sale.line', 'order_id', string='Order Lines',
                                 states={'done': [('readonly', True)]}, copy=True,
                                 auto_join=True,track_visibility='onchange')
    transaction_type = fields.Selection([('Direct','Direct'),('Warehouse', 'Warehouse')], string='Transaction Type',
                                 copy=False, required=True, index=True, track_visibility='onchange', default='Warehouse')
    amount_untaxed = fields.Float(compute=_amount_all_wrapper, string='Untaxed Amount',track_visibility='onchange')
    tax_value = fields.Float(compute=_tax_amount, string='Taxes',track_visibility='onchange')
    total_amount = fields.Float(compute=_get_total_amount, string='Total Amount',track_visibility='onchange')
    so = fields.Char('Party PO No.',track_visibility='onchange')
    invoice_count = fields.Integer(string='Export Invoice', compute='_compute_export_ids',track_visibility='onchange')
    transaction_ids = fields.One2many('my.invoice', 'sale_id', string='Transactions', track_visibility='onchange')
    ordered_qty = fields.Float('Ordered Qty',compute='_compute_ordered_qty',  track_visibility='onchange')
    exported_qty = fields.Float('Exported Qty', compute='_compute_exported_qty', track_visibility='onchange')
    productTariffDesc = fields.Text('Product TariffDesc.',default='OTHER PARTS AND ACCESSORIES OF MOTOR VEHICLE OF HEADINGS 8701 TO 8705')
    ship_from = fields.Many2one('ship.from',string="Ship From")
    # ship_id=fields.Many2one('ship.from','Ship From')




class SaleLine(models.Model):
    _name = "my.sale.line"

    def get_subtotal(self):
        total_price = 0.00
        for val in self:
            if val.qty:
                total_price = (val.qty * val.unit_price)
                val.write({'price_subtotal1':total_price})
                val.price_subtotal = total_price

    @api.onchange('product_id')
    def onchange_product_id(self):
        unit_price = 0.0
        rate = 0.0
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.unit_price = self.product_id.list_price
            self.part_id = self.product_id.part_id.id

    def _compute_export_qty(self):
        qty =0.0
        for val in self:
            if val.export_qty:
                val.compute_export_qty =  val.export_qty



    order_id = fields.Many2one('my.sale','Id',track_visibility='onchange')
    product_id = fields.Many2one('my.product','Product',track_visibility='onchange')
    part_id = fields.Many2one('my.part', String="Part No.",track_visibility='onchange')
    hsn_code = fields.Char('HSN Code',track_visibility='onchange')
    uom_id = fields.Many2one('my.uom','UOM',track_visibility='onchange')
    qty = fields.Float('Qty', default=1,track_visibility='onchange')
    compute_export_qty = fields.Float('Exported Qty',compute='_compute_export_qty',  track_visibility='onchange')
    export_qty = fields.Float('Export Qty', default=0, track_visibility='onchange')
    unit_price = fields.Float('Unit Price',digits=(16,4),track_visibility='onchange')
    tax_id = fields.Many2many('my.tax', string='Taxes',track_visibility='onchange')
    price_subtotal = fields.Float(compute = get_subtotal, string='Subtotal',track_visibility='onchange')
    price_subtotal1 = fields.Float(string='Subtotal',track_visibility='onchange')








