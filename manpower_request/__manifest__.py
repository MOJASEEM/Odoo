
{
    'name': 'Man Power Request',
    'version': '1.0',
    'author': 'jaseem',
    'summary': 'Manage Man Power Requests and Departments',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/department_view.xml',
        'views/job_views.xml',
        'views/man_views.xml',
        'views/qual_views.xml',
        'views/skills_views.xml',
        'views/menu.xml'
    ],
    'installable': True,
    'application': True,
}