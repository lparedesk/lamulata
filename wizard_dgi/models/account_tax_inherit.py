# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountTaxInheritDGI(models.Model):
    _inherit = 'account.tax'

    code_igv_dgi = fields.Char(
        string=u'Código de impuesto DGI'
    )
    is_extent = fields.Boolean(
        string='Exento'
    )
