import time
from odoo import api, fields, models
from datetime import datetime,timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class SaleWizard(models.TransientModel):
    _name = 'sale.wizard'

    sale_wizard_line = fields.One2many('sale.wizard.line','wizard_id',string='Lines')




    @api.model
    def default_get(self, fields):
        obj = self.env['my.sale'].browse(self.env.context.get('active_id'))
        res = super(SaleWizard, self).default_get(fields)
        moves = []
        res = {}
        if 'sale_wizard_line' in fields:
            query = "select bol.id , bol.product_id, bol.unit_price, bol.qty, bol.export_qty, bol.uom_id, bol.part_id from my_sale_line as bol left join my_sale as bo on bo.id = bol.order_id where  bo.id = '" + str(
                obj.id) + "'"

            self.env.cr.execute(query)
            temp = self.env.cr.fetchall()
            for val1 in temp:
                if val1[3] > val1[4]:
                    dict2 = {}
                    dict2['order_id'] = val1[0]
                    dict2['product_id'] = val1[1]
                    dict2['unit_price'] = val1[2]
                    dict2['qty'] = val1[3] - val1[4]
                    dict2['actual_qty'] = val1[3] - val1[4]
                    dict2['uom_id'] = val1[5]
                    dict2['part_id'] = val1[6]
                    moves.append(dict2)
            res['sale_wizard_line'] = [(0, 0, x) for x in moves]
        return res





    def create_invoice(self):
        var=False
        for i in self.sale_wizard_line:
            if i.select:
                var=True
        if var==True:
            product_list = []
            schedule_invoice_obj = self.env['my.sale'].browse(self.env.context.get('active_id'))
            if self.sale_wizard_line:
                sale = self.env['my.invoice'].create({'partner_id': schedule_invoice_obj.partner_id.id,'ship_to': schedule_invoice_obj.ship_to.id,'payment_term_id': schedule_invoice_obj.payment_term_id.id,'sale_id':schedule_invoice_obj.id,
                                                      'date':datetime.today(),'transaction_type':schedule_invoice_obj.transaction_type, 'ship_from': schedule_invoice_obj.ship_from.id, 'party_po':schedule_invoice_obj.so, 'productTariffDesc': schedule_invoice_obj.productTariffDesc})
                for val in self.sale_wizard_line:
                    if val.select and val.qty != 0:
                        if val.qty <= val.actual_qty:
                            self.env['my.invoice.line'].create({'order_id':sale.id,'product_id': val.product_id.id,'name': val.product_id.name,
                                                                 'uom_id':val.uom_id.id,
                                                        'qty':val.qty,'unit_price':val.unit_price,
                                                      'part_id': val.product_id.part_id.id})
                        else:
                            raise UserError(('Order limit is Over'))
            return {
                'name': ('my.invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'my.invoice',
                'res_id': sale.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'nodestroy': True,
            }
        else:
            raise UserError(('Please Tick Lines'))

class SaleWizardLine(models.TransientModel):
    _name = 'sale.wizard.line'

    wizard_id = fields.Many2one('sale.wizard','Wizard')
    select = fields.Boolean('Select')
    product_id = fields.Many2one('my.product', 'Product', track_visibility='onchange')
    part_id = fields.Many2one('my.part', String="Part No.", track_visibility='onchange')
    uom_id = fields.Many2one('my.uom', 'UOM', track_visibility='onchange')
    qty = fields.Float('Qty', default=1, track_visibility='onchange')
    actual_qty = fields.Float('Qty', default=1, track_visibility='onchange')
    unit_price = fields.Float('Unit Price',digits=(16,4), track_visibility='onchange')