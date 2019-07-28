
import xlsxwriter
import xlwt as xlwt
def trans_report(data=[[1,2,3,4,5,6]],rname=""):
    workbook = xlsxwriter.Workbook('Transaction_report.xlsx')
    worksheet = workbook.add_worksheet()
    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})
    # Write some data headers.
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        })
    merge_format3 = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        })
    merge_format3.set_font_size(20)
    merge_format1 = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
        })
    # style = xlwt.easyxf('font: bold 1,height 280;')
    worksheet.merge_range('B1:E3', 'Stock Transaction Repot(%s)'%rname, merge_format3)
    a="\n"
    worksheet.write_column('F1',['From Date :-'],merge_format)
    worksheet.write_column('F3',['To Date :-'],merge_format)
    worksheet.write_column('F2',[' '],merge_format)
    # worksheet.write_column('A1','   ',merge_format)
    worksheet.set_column('A4:A30', 15)
    worksheet.merge_range('A4:A5','Sr No.'.format(a),merge_format)
    worksheet.set_column('B4:B30',50)
    worksheet.merge_range('B4:B5', 'Customer Name',merge_format)
    worksheet.set_column('C4:C30',50)
    worksheet.merge_range('C4:C5', 'Product Name',merge_format)
    worksheet.set_column('D4:D30',20)
    worksheet.merge_range('D4:D5', 'Qty',merge_format)
    worksheet.set_column('E4:E30',20)
    worksheet.merge_range('E4:E5', 'Uom',merge_format)
    worksheet.set_column('F4:F30',30)
    worksheet.merge_range('F4:F5', 'Reference',merge_format)
    #worksheet.merge_range('A1:C3', '',merge_format)
    worksheet.insert_image('A1', 'SEBROS/slogo.jpg', {'x_scale': .2, 'y_scale': .3})
    x=6
    for i in data:
        worksheet.write_row('A%s'%str(x),i,merge_format)
        x+=1
    workbook.close()


