import xlsxwriter
import xlwt as xlwt
import datetime

def stock_report(data=[[1,2,3,4],[8,7,6,5],[1,2,3,4]],type='IN HAND'):

    workbook = xlsxwriter.Workbook('Warehouse_Stock.xlsx')
    worksheet = workbook.add_worksheet()
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 20,
        })
    merge_format1 = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        })
    h=['Sr No.','Product Name','Quantity','UOM']
    worksheet.set_column('A1:A30',15)
    worksheet.set_column('B1:B30',55)
    worksheet.set_column('C1:D1',22)
    worksheet.set_column('E1:E30',30)
    # worksheet.set_row()
    worksheet.merge_range('B1:C3', '%s WAREHOUSE STOCK REPORT'%(type), merge_format)
    t= datetime.datetime.today().strftime('%d-%m-%Y')
    worksheet.merge_range('D1:D3', 'Date :- %s'%t, merge_format1)
    worksheet.write_row('A4',h,merge_format1)
    worksheet.insert_image('A1:A3', 'SEBROS/slogo.jpg', {'x_scale': .2, 'y_scale': .3})
    x=5
    for i in data:
        worksheet.write_row('A%s'%str(x),i,merge_format1)
        x+=1
    workbook.close()