# -*- coding: utf-8 -*-
{
    "name": "Formulario 2181 DGI",
    'summary': "Genera formulario 2181 segun DGI",
    'version': '12.0.1.1',
    "category": "Localizacion Uruguay",
    "author": "Kreilabs Team",
    'website': 'www.kreilabs.com',
    "license": "AGPL-3",
    'depends': [
            'base',
            'account',
            'date_range'
    ],
    'data': [
        'wizard/account_invoice_wizard.xml',
        'views/account_journal_dgi_form.xml',
        'views/account_tax_dgi_form.xml'
       ],
    "application": False,
    "installable": True,
}
