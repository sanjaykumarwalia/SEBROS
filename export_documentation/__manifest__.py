{

            'name': 'export_documentation',
            'version': '1.0',
            'author': 'ERP Softtech Solution',
            'depends': ['base','mail'],
            'category': ' ',

            'description': '',
            'data': [
				'views/masters_views.xml',
				'views/po_views.xml',
				'views/exp_invoice_template.xml',
				'views/stock_view.xml',
				'views/in_transit_view.xml',
				'views/packing_list_template.xml',
				'views/sequence_view.xml',
				'views/res_company_view.xml',
				'views/invoice_view.xml',
				'views/pod_view.xml',
				'views/payment_receive_view.xml',
				'reports/exp_invoice.xml',
				'reports/packing_list.xml',
				'wizard/reports_wizard.xml',
				'wizard/sale_wizard_view.xml',
				'security/for_security.xml',
				'security/ir.model.access.csv',

],
            'website': 'www.erpsofttech.com',
            'demo_xml': [],
            'js': [],
            'css': [],

            'installable': True,
            'auto-installable': False,
            'active': False,
        }
