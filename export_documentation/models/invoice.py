from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
# class MyTransport(models.Model):
#     _name="my.transport"
#     _order = "id desc"


class MyInvoice(models.Model):
    _name="my.invoice"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('invoice_code')
        vals['name'] = 'EXP/19-20/' + str(seq)
        sum_id = super(MyInvoice, self).create(vals)
        return sum_id
    @api.depends('order_line','order_line.price_subtotal')
    def _amount_all_wrapper(self):

        for val in self:
            total_amount = 0.00
            if val.order_line:
                for val1 in val.order_line:
                    total_amount = total_amount + val1.price_subtotal
                    val.amount_untaxed = round(total_amount,2)

    @api.depends('order_line', 'order_line.qty')
    def _get_total_qty(self):

        for val in self:
            total_qty = 0.00
            if val.order_line:
                for val1 in val.order_line:
                    total_qty = total_qty+val1.qty
                    val.total_qty = total_qty

    @api.depends('order_line.tax_id')
    def _tax_amount(self):

        for val in self:
            total_tax = 0.00
            if val.order_line:
                for val1 in val.order_line:
                    amount = 0.0
                    if val1.tax_id:
                        for val2 in val1.tax_id:
                            amount = round((amount + val2.amt),2)
                    else:
                        amount = val1.tax_id.amt
                    total_tax = total_tax + (val1.qty * val1.unit_price)* amount / 100
                    val.tax_value = round(total_tax,2)

    @api.depends('amount_untaxed','tax_value')
    def _get_total_amount(self):
        for val in self:
            total_amount=0.0
            total_amount = val.amount_untaxed
            val.total_amount = round(total_amount,2)
    @api.depends('order_line')
    def _get_nt_weight(self):
        for val in self:
            total_weight = 0.00
            for val1 in val.order_line:
                if val1.product_id:
                    total_weight = total_weight + round(val1.qty  * val1.product_id.weight)
        val.nt_weight = total_weight
    @api.depends('order_line')
    def _get_tariff(self):
        # tariff_code = self.product_id.tariff
        # print(self.product_id.tariff)

        for val in self:
            tariff=''
            for val1 in val.order_line:
                if val1.product_id:
                    tariff =  val1.product_id.tariff
                    # print('00000000000000= ',tariff)
            val.tariff_code = tariff

    @api.depends('packing_list_line')
    def _get_gr_weight(self):
        total_weight = 0.00
        for val in self:
            for x in val.packing_list_line:
                total_weight+=x.gross_weight
            val.gr_weight=total_weight
            return True


    @api.multi
    def action_confirm(self):
        for val in self.order_line:
            lqty=0.0
            for val1 in self.packing_list_line:
                if val.product_id.id==val1.product_id.id:
                    lqty+=val1.qty
            if lqty!=val.qty:
                raise UserError(('Packing list line Qty For Product - %s is not matched with Invoiced Qty.'%val.product_id.name))

        if self.transaction_type=='Warehouse':
            if self.order_line:
                for val in self.order_line:
                    stock_obj = self.env['in.transit'].search([('product_id', '=', val.product_id.id), ('part_id', '=', val.product_id.part_id.id ), ('uom_id', '=', val.uom_id.id)])
                    if stock_obj:
                        stock_obj.write({'qty': stock_obj.qty + val.qty,'reference': self.name})
                    else:
                        stock = self.env['in.transit'].create({'product_id': val.product_id.id, 'part_id': val.product_id.part_id.id ,'uom_id': val.uom_id.id,'qty': (val.qty)})
            
            if self.sale_id:
                # self.ship_from=self.sale_id.ship_from
                # print('0000dd0d00000',self.sale_id.ship_from)
                for val1 in self.order_line:
                    sale_line_obj = self.env['my.sale.line'].search([('product_id', '=', val1.product_id.id), ('part_id', '=', val1.product_id.part_id.id ),('uom_id', '=', val1.uom_id.id),('order_id', '=', self.sale_id.id)])
                    sale_line_obj.write({'export_qty':sale_line_obj.export_qty + val1.qty})

            self.write({'state': 'confirm'})
        elif self.transaction_type=='Direct':
            self.write({'state': 'done'})
        else:
            if self.sale_id:
                for val1 in self.order_line:
                    sale_line_obj = self.env['my.sale.line'].search([('product_id', '=', val1.product_id.id), ('part_id', '=', val1.product_id.part_id.id ),('uom_id', '=', val1.uom_id.id),('order_id', '=', self.sale_id.id)])
                    sale_line_obj.write({'export_qty':sale_line_obj.export_qty + val1.qty})
            self.write({'state': 'confirm'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_done(self):
        if self.transaction_type=='Warehouse':
            if self.order_line:
                for val in self.order_line:
                    stock_obj = self.env['my.stock'].search(
                        [('product_id', '=', val.product_id.id), ('part_id', '=', val.product_id.part_id.id ), ('uom_id', '=', val.uom_id.id)])
                    stock_obj1 = self.env['in.transit'].search(
                        [('product_id', '=', val.product_id.id), ('part_id', '=', val.product_id.part_id.id ), ('uom_id', '=', val.uom_id.id)])
                    if stock_obj:
                        stock_obj.write({'qty': stock_obj.qty + val.qty, })
                    else:
                        stock = self.env['my.stock'].create(
                            {'product_id': val.product_id.id, 'part_id': val.product_id.part_id.id, 'uom_id': val.uom_id.id, 'qty': (val.qty),
                             'reference': self.name})
                    if stock_obj1:
                        stock_obj1.write({'qty': stock_obj1.qty - val.qty})
                    else:
                        stock1 = self.env['in.transit'].create(
                            {'product_id': val.product_id.id, 'part_id': val.product_id.part_id.id, 'uom_id': val.uom_id.id, 'qty': (val.qty)})

        self.write({'state': 'done'})
        return True
    @api.depends('payment')
    def get_due(self):
        amtt = 0
        for val in self:
            if val.total_amount:
                amtt=(val.total_amount-val.payment)
            val.write({'due_amount1':round(amtt,2)})
            val.due_amount=round(amtt,2)



    name = fields.Char(string='Invoice No.', required=True, copy=False, readonly=False,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: ('New'),track_visibility='onchange')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
        ('done', 'Locked'),

    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    date = fields.Date(string='Date', required=True, readonly=True, index=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Date.today, track_visibility='onchange',)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    partner_id = fields.Many2one('my.partner', string='Customer', readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='onchange',)
    ship_to = fields.Many2one('my.partner', string='Ship To', readonly=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True,
                                 change_default=True, index=True, track_visibility='onchange',)
    delivery_date = fields.Datetime(string='Delivery Date', track_visibility='onchange',)
    payment_term_id = fields.Many2one('my.payment.term', string='Payment Terms', track_visibility='onchange')

    order_line = fields.One2many('my.invoice.line', 'order_id', string='Order Lines',
                                 states={'done': [('readonly', True)]}, copy=True,
                                 auto_join=True, track_visibility='onchange',)
    packing_list_line = fields.One2many('packing.list.line', 'order_id', string='Packing List Lines',
                                 states={'done': [('readonly', True)]}, copy=True,
                                 auto_join=True, track_visibility='onchange', )
    transaction_type = fields.Selection([('Direct', 'Direct'), ('Warehouse', 'Warehouse')], string='Transaction Type',
                                        copy=False, required=True,index=True, track_visibility='onchange',
                                        default='Warehouse')
    amount_untaxed = fields.Float(compute=_amount_all_wrapper, string='Untaxed Amount',track_visibility='onchange')
    tax_value = fields.Float(compute=_tax_amount, string='Taxes',track_visibility='onchange')
    total_amount = fields.Float(compute=_get_total_amount, string='Total Amount',track_visibility='onchange')
    sale_id = fields.Many2one('my.sale','Sale Order', track_visibility='onchange',)
    party_po= fields.Char(string="Party Po No.")
    nt_weight = fields.Float(compute=_get_nt_weight,string='NT. Weight', track_visibility='onchange')
    gr_weight = fields.Float(compute=_get_gr_weight,string='GR. Weight', track_visibility='onchange')
    productTariffDesc =fields.Text('Part Tariff Desc')
    delivery_term=fields.Selection([
        ('fob', 'FOB'),
        ('exw', 'EXW'),
        ('cnf', 'C&F'),
        ('cif', 'CIF'),
        ('fca', 'FCA Free Carrier Faridabad,India'),
        ])
    # delivery_term = fields.Char('Delivery Term',track_visibility='onchange')
    tariff_code = fields.Char(compute=_get_tariff,string='Tariff Code',track_visibility='onchange')
    ship_from = fields.Many2one('ship.from',string="Ship From")
    # ship_from = fields.Selection([
    #     ('fob', 'FOB'),
    #     ('exw', 'EXW'),
    #     ('cnf', 'C&F'),
    #     ('cif', 'CIF'),
    #     ('fca', 'FCA Free Carrier Faridabad,India'),])

    transportation_mode = fields.Char('Transport Mode',track_visibility='onchange')
    # transportation_mode = fields.Many2one('my.transport.bymode','Transport Mode', track_visibility='onchange')
    remark = fields.Text('Remark',track_visibility='onchange')
    attention = fields.Char('Attention To',track_visibility='onchange')
    no_of_palletsNew = fields.Char(string='No. Of Pallets')
    no_of_pallets = fields.Integer(string='No. Of Pallets', track_visibility='onchange')
    payment = fields.Float('Payment', default=0.00)
    due_amount = fields.Float('Due Amount', compute = 'get_due')
    due_amount1 = fields.Float('Due Amount',)
    total_qty = fields.Float('Qty',compute = '_get_total_qty')






class MyInvoiceLine(models.Model):
    _name = "my.invoice.line"
    @api.depends('qty')
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
            self.qty=self.product_id.std_qty_per_pallet

    @api.onchange('pallets')
    def onchange_pallets(self):
        self.qty = self.product_id.std_qty_per_pallet *self.pallets

    order_id = fields.Many2one('my.invoice','Id',track_visibility='onchange')
    product_id = fields.Many2one('my.product','Product',track_visibility='onchange')
    part_id = fields.Many2one('my.part',string='Part No.', track_visibility='onchange')
    hsn_code = fields.Char('HSN Code',track_visibility='onchange')
    uom_id = fields.Many2one('my.uom','UOM',track_visibility='onchange')
    pallets = fields.Float(string='No of Pallets', track_visibility='onchange',default=1)
    qty = fields.Float('Qty', default=1,track_visibility='onchange')
    unit_price = fields.Float('Unit Price',digits=(16,4), track_visibility='onchange')
    tax_id = fields.Many2many('my.tax', string='Taxes',track_visibility='onchange')
    price_subtotal = fields.Float(compute = get_subtotal, string='Subtotal',track_visibility='onchange')
    price_subtotal1 = fields.Float(string='Subtotal',track_visibility='onchange')

class PackingListLine(models.Model):
    _name = "packing.list.line"

    @api.onchange('product_id','part_id')
    def onchange_product_id(self):
        self.qty = self.product_id.std_qty_per_pallet

        product_list = []
        part_list = []
        if self.order_id.order_line:
            for val in self.order_id.order_line:
                product_list.append(val.product_id.id)
                part_list.append(val.product_id.part_id.id)
            if self.product_id:
                self.uom_id = self.product_id.uom_id.id
                self.part_id = self.product_id.part_id.id
            if self.part_id:
                self.product_id = self.product_id.id
                self.uom_id = self.product_id.uom_id.id

            domain = {'product_id': [('id', '=', product_list)],'part_id': [('id', '=', part_list)]}
            return {'domain': domain}

    @api.depends('qty')
    def get_netweight(self):
        for val in self:
            if val.qty:
                val.net_weight = round(val.product_id.weight*val.qty)

    @api.depends('net_weight','pallet_weight')
    def get_grossweight(self):
        for val in self:
            if val.net_weight:
                val.gross_weight = round(val.net_weight + val.pallet_weight)

    # @api.depends('qty')
    # def calulateqty(self):
    #     for xx in self:
    #         for val in xx.order_id.order_line:
    #             if val.product_id.id==xx.product_id.id:
    #                 tqty=val.qty
    #                 lqty=0.0
    #                 print('xxxxxxxxxxxxxxxxx',tqty)
    #                 for val1 in xx.order_id.packing_list_line:
    #                     print('yyyyyyyyyyyyyyyyy',val1.qty)
    #                     if val.product_id.id==val1.product_id.id:
    #                         lqty=lqty+val1.qty
    #                         print('zzzzzzzzzz',lqty)
    #                 if lqty>tqty:
    #                     raise UserError(('Total Packing List Qty is Greater than Invoice Quantity'))








    order_id = fields.Many2one('my.invoice', 'Id', track_visibility='onchange')
    lot_no= fields.Char(string='Lot No.')
    description = fields.Char(string='Description')
    net_weight = fields.Float('Net Weight', compute = get_netweight)
    pallet_weight = fields.Float('Pallet Weight')
    gross_weight = fields.Float('Gross Weight', compute = get_grossweight)
    product_id = fields.Many2one('my.product', 'Product', track_visibility='onchange')
    part_id = fields.Many2one('my.part','Part No.',track_visibility='onchange')
    qty = fields.Float('Quantity in each')
    uom_id = fields.Many2one('my.uom', 'UOM')

class ShipFrom(models.Model):
    _name = "ship.from"

    name= fields.Char(string="Ship From")