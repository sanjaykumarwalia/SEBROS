
import xlsxwriter

# Create a workbook and add a worksheet.
import xlwt as xlwt
def outstanding(data=[[1,2,3,4,5,6,7,8]]):
    workbook = xlsxwriter.Workbook('Outstanding.xlsx')
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


    style = xlwt.easyxf('font: bold 1,height 280;')

    worksheet.merge_range('A1:H4', 'OUTSTANDING REPORT', merge_format3)

    worksheet.set_column('A5:A30', 10)
    worksheet.merge_range('A5:A7', 'Sr No.',merge_format)

    worksheet.set_column('B5:B30', 60)
    worksheet.merge_range('B5:B7', 'Customer',merge_format)

    worksheet.set_column('C5:C30', 25)
    worksheet.merge_range('C5:C7', 'INVOICE/POD',merge_format)

    worksheet.set_column('D5:D30',25)
    worksheet.merge_range('D5:D7', 'DATE',merge_format)

    worksheet.set_column('E5:E30',20)
    worksheet.merge_range('E5:E7', 'AMOUNT',merge_format)

    worksheet.set_column('F5:F30',30)
    worksheet.merge_range('F5:F7', 'PAID AMOUNT',merge_format)

    worksheet.set_column('G5:G30',25)
    worksheet.merge_range('G5:G7', 'DUE AMOUNT',merge_format)

    worksheet.set_column('H5:H30',25)
    worksheet.merge_range('H5:H7', 'Reference',merge_format)

    x=8
    for l in data:
        worksheet.write_row('A%d'%x,l,merge_format)
        x+=1



    # worksheet.merge_range('A1:B3', '',merge_format)
    # worksheet.insert_image('A1', '/home/gaurav/Desktop/2019/Apr/16Apr2019/logoscw.jpeg', {'x_scale': 2.5, 'y_scale': 2.5})

    workbook.close()

outstanding()
