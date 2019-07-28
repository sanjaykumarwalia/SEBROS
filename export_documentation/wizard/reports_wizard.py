import time
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import base64
from .report import *
from .trans import *
from .outstanding import *

class ReportsWizard(models.TransientModel):
    _name = "reports.wizard"

    @api.one
    def _get_template(self):
        self.contract_template = base64.b64encode(open("Transaction_report.xlsx", "rb").read())

    @api.multi
    def trans_report(self):
        if self.transaction_type=='Direct':
            l=[]
            if self.partner_id:
                x = self.env['my.invoice'].search([('partner_id', '=', self.partner_id.name),('date', '>=', self.from_date), ('date', '<=', self.to_date),('state', '=', 'done'),('transaction_type', '=', 'Direct')])
            else:
                x = self.env['my.invoice'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date),('state', '=', 'done'),('transaction_type', '=', 'Direct')])
            s=0
            if x:
                for var in x:
                    h = self.env['my.invoice.line'].search([('order_id', '=', var.id)])
                    if h:
                        for n in h:
                            l.append([s+1,var.partner_id.name,n.product_id.name,n.qty,n.uom_id.name,var.name])
                            s+=1
                        trans_report(data=l,rname="Direct")
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'contract',
                    'url': '/web/content/reports.wizard/%s/contract_template/Transaction_report.xlsx?download=true' % (
                        self.id),
                }
            else:
                raise UserError('NO DATA AVAILABLE')


        elif self.transaction_type=='Warehouse':
            l=[]
            if self.partner_id:
                x = self.env['my.invoice'].search([('partner_id', '=', self.partner_id.name),('date', '>=', self.from_date), ('date', '<=', self.to_date),('state', 'in', ['done','confirm']),('transaction_type', '=', 'Warehouse')])
            else:
                x = self.env['my.invoice'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date),('state', 'in', ['done','confirm']),('transaction_type', '=', 'Warehouse')])
            s=0
            if x:
                for var in x:
                    h = self.env['my.invoice.line'].search([('order_id','=',var.id)])
                    if h:
                        for n in h:
                            l.append([s+1,var.partner_id.name,n.product_id.name,n.qty,n.uom_id.name,var.name])
                            s+=1
                        trans_report(data=l,rname="Warehouse")
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'contract',
                    'url': '/web/content/reports.wizard/%s/contract_template/Transaction_report.xlsx?download=true' % (
                        self.id),
                }
            else:
                raise UserError('NO DATA AVAILABLE')

        elif self.transaction_type=='POD':
            l=[]
            if self.partner_id:
                x = self.env['my.pod'].search([('partner_id', '=', self.partner_id.name),('date', '>=', self.from_date), ('date', '<=', self.to_date),('state', '=', 'done')])
            else:
                x = self.env['my.pod'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date),('state', '=', 'done')])
            s=0
            if x:
                for var in x:
                    h = self.env['my.pod.line'].search([('order_id', '=', var.id)])
                    if h:
                        for n in h:
                            l.append([s+1,var.partner_id.name,n.product_id.name,n.qty,n.uom_id.name,var.reference])
                            s+=1
                        trans_report(data=l,rname="POD")
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'contract',
                    'url': '/web/content/reports.wizard/%s/contract_template/Transaction_report.xlsx?download=true' % (
                        self.id),
                        }
            else:
                raise UserError('NO DATA AVAILABLE')

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    partner_id = fields.Many2one('my.partner','Customer')
    transaction_type = fields.Selection([('Direct', 'Direct'), ('Warehouse', 'Warehouse'), ('POD', 'POD')], string='Transaction Type',
                                        copy=False, required=True,index=True,default='Warehouse')
    contract_template = fields.Binary('Template', compute="_get_template")


class StockReport(models.TransientModel):
    _name = "stock.report"

    @api.one
    def _get_template(self):
        self.contract_template = base64.b64encode(open("Warehouse_Stock.xlsx", "rb").read())


    @api.multi
    def stock_report(self):

        if self.stock_type=='in hand':
            x = self.env['my.stock'].search([('qty', '>', 0)])
            if x:
                i = 0
                z = [[j + 1, l.product_id.name, l.qty, l.uom_id.name] for j, l in enumerate(x)]
                stock_report(data=z, type='IN HAND')
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'contract',
                    'url': '/web/content/stock.report/%s/contract_template/Warehouse_Stock.xlsx?download=true' % (
                        self.id),
                }
            else:
                raise UserError('NO DATA AVAILABLE')


        elif self.stock_type=='in transit':
            x = self.env['in.transit'].search([('qty', '>', 0)])
            if x:
                i = 0
                z = [[j + 1, l.product_id.name, l.qty, l.uom_id.name] for j, l in enumerate(x)]
                stock_report(data=z, type='IN TRANSIT')
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'contract',
                    'url': '/web/content/stock.report/%s/contract_template/Warehouse_Stock.xlsx?download=true' % (
                        self.id),
                }
            else:
                raise UserError('NO DATA AVAILABLE')

    stock_type=fields.Selection([('in transit', 'In Transit'), ('in hand', 'In Hand')], string='Stock Type',
                                        copy=False, required=True,index=True,default='in hand')
    contract_template = fields.Binary('Template', compute="_get_template")

class Outstanding(models.TransientModel):
    _name = "outstanding"

    @api.one
    def _get_template(self):
        self.contract_template = base64.b64encode(open("Outstanding.xlsx", "rb").read())

    @api.multi
    def outstanding(self):
        if self.transaction_type=='Warehouse':
            l = []
            if self.partner_id:
                x = self.env['my.pod'].search(
                    [('partner_id', '=', self.partner_id.name), ('date', '>=', self.from_date),
                     ('date', '<=', self.to_date), ('state', '=', 'done')])
            else:
                x = self.env['my.pod'].search(
                    [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('state', '=', 'done')])
            s = 0
            if x:
                for var in x:
                    l.append([s+1,var.partner_id.name,var.name,str(var.date),round(var.total_amount,2),round(var.payment,2),round(var.amount_due,2),var.reference])
                    # print(l)
                    s += 1
                outstanding(data=l)
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'contract',
                    'url': '/web/content/outstanding/%s/contract_template/Outstanding.xlsx?download=true' % (
                        self.id),
                }
            else:
                raise UserError('NO DATA AVAILABLE')
        elif self.transaction_type=='Direct':
            l = []
            if self.partner_id:
                x = self.env['my.invoice'].search(
                    [('partner_id', '=', self.partner_id.name), ('date', '>=', self.from_date),
                     ('date', '<=', self.to_date), ('state', '=', 'done')])
            else:
                x = self.env['my.invoice'].search(
                    [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('state', '=', 'done')])
            s = 0
            if x:
                for var in x:
                    l.append([s + 1, var.partner_id.name,var.name,str(var.date),round(var.total_amount,2),round(var.payment,2),round(var.due_amount,2),var.sale_id.so])
                    s+=1
                    outstanding(data=l)
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'contract',
                    'url': '/web/content/outstanding/%s/contract_template/Outstanding.xlsx?download=true' % (
                        self.id),
                }
            else:
                raise UserError('NO DATA AVAILABLE')



    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    partner_id = fields.Many2one('my.partner', 'Customer')
    transaction_type = fields.Selection([('Warehouse', 'Warehouse'), ('Direct', 'Direct')], string='Stock Type',
                                  copy=False, required=True, index=True, default='Warehouse')
    contract_template = fields.Binary('Template', compute="_get_template")
