# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountJournalInheritDGI(models.Model):
    _inherit = 'account.journal'

    form_2181_dgi = fields.Boolean(
        string='Formulario 2181 DGI'
    )
    sign = fields.Selection(
        string=u'Dirección',
        selection=[
            ('none', 'Ninguno'),
            ('in', 'Ingreso'),
            ('out', 'Salida'),
        ], default='none'
    )