
{
    'name': 'Firmer Print',
    'version': '1.0',
    'author': 'jaseem',
    'summary': 'Firmer Print',
    'depends': ['base','account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_invoice.xml',
    ],
    'installable': True,
    'application': True,
}