{
    'name': 'Real Estate',
    'summary': 'The Real Estate Advertisement module',
    'description': 'A module to manage real estate properties.',
    'depends': ['base'],
    'application': True,
    'installable': True,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/security_groups.xml',
        'views/estate_property_views.xml',
        'views/res_users_views.xml',
        'report/estate_property_reports.xml'
    ],
    'assets':{
        'web.assets_backend':[
            'estate/static/src/js/estate_dashboard.js',
            'estate/static/src/xml/estate_dashboard.xml'
        ]
    }
}