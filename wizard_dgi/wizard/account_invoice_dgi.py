
from datetime import date, datetime
import xlwt
import base64
import os
import time
from odoo import models, fields
from odoo import api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class SaleBookReport(models.TransientModel):
    _name = 'account.invoice.dgi'

    date = fields.Date(
        string=u'Fecha Presentación',
        default=fields.Date.context_today,
    )

    state = fields.Selection(
        [
            ('stop', 'Pendiente'),
            ('done', 'Realizado')
        ],
        string="Estado",
        default='stop'
    )

    period = fields.Many2one(
        string='Mes',
        comodel_name='date.range'
    )

    txt_filename = fields.Char(
        string="Beta",
        readonly=True
    )
    print_extra = fields.Boolean(
        string="Imprimir asiento"
    )

    txt_binary = fields.Binary('Form 2181 DGI', readonly=True)

    @api.multi
    def generate_report(self):
        str_fin_linea = '\n'
        str_fin = ';'
        str_ruta = ''
        str_nombre_archivo = ''.join(['BETA', ".txt"])
        contend = ''
        account_move_line = self.env['account.move.line'].search([
            ('move_id.date', '>=', self.period.date_start),
            ('move_id.date', '<=', self.period.date_end),
            ('move_id.journal_id.form_2181_dgi', '=', True),
        ])
        #aml_list=[13,14,15,16,17,18] # caso ventas
        #aml_list=[34,35,36,37,38,39] # caso compras con exento
        #aml_list=[40,41,42,43,44,45] # caso Nota de credito venta
        #aml_list=[46,47,48,49,50,51] # caso Nota de credito compra
        #aml_list=[52,53,54,55] # Gasto OJO, asientos simples
        aml_list=[]
        if len(aml_list) > 0:
            account_move_line = self.env['account.move.line'].browse(aml_list)
        move_name=''
        for aml in account_move_line:
            if aml.partner_id.vat:
                str_linea_1 = ''
                if self.print_extra:
                    move_name = aml.move_id.name+';' or ''
                if aml.journal_id.form_2181_dgi:
                    amount = self._get_total_line(aml)
                    if amount:
                        code_tax = self._get_tax_code(aml)
                        date_asiento = aml.move_id.date.strftime('%Y-%m')
                        date_generate = self.date.strftime('%Y-%m')
                        str_linea_1 = ''.join(
                            [
                                str_linea_1,
                                move_name,
                                aml.move_id.company_id.vat,
                                ';',
                                '02181',
                                ';',
                                date_asiento.replace("-", "") or "",
                                ';',
                                aml.partner_id.vat or "",
                                ';',
                                date_generate.replace("-", "") or "",
                                ';',
                                code_tax or "",
                                ';',
                                str(amount),
                                str_fin
                            ]
                        )
                        contend = contend + u''.join(
                            [str_linea_1, str_fin_linea])
        if str_ruta:
            if not os.path.exists('/tmp'):
                os.makedirs(str_ruta)
        str_ruta_archivo = os.path.join('/tmp' or '', str_nombre_archivo)
        fichero = open(str_ruta_archivo, "w")
        fichero.write(contend)
        fichero.close()
        file = open(str_ruta_archivo, "rb")
        out = file.read()
        self.write({
            'txt_filename': str_nombre_archivo,
            'txt_binary': base64.b64encode(out),
            'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        })

        self.state = 'done'

        view = self.env.ref('wizard_dgi.view_wizard_dgi_form')
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.dgi',
            'res_id': self.id,
            'view_id': view.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def _get_total_line(self, aml):
        amount=0
        total_lenght = 12
        if aml.tax_line_id:
            if aml.credit != 0.0:
                amount = aml.credit
                if aml.move_id.journal_id.sign == "out":
                    amount = amount * -1
            elif aml.debit != 0.0:
                amount = aml.debit
                if aml.move_id.journal_id.sign == "in":
                    amount = amount * -1
            else:
                amount = 0
        for tax_applied in aml.tax_ids:
            if tax_applied.is_extent:
                if aml.credit != 0.0:
                    amount = aml.credit
                    if aml.move_id.journal_id.sign == "out":
                        amount = amount * -1
                elif aml.debit != 0.0:
                    amount = aml.debit
                    if aml.move_id.journal_id.sign == "in":
                        amount = amount * -1
                else:
                    amount = 0
        amount = int(amount)
        if amount == 0:
            amount = False
        else:
            if amount < 0:
                amount = str(amount).zfill(total_lenght+1)
            else:
                amount = str(amount).zfill(total_lenght)
        return amount

    @api.multi
    def _get_tax_code(self, aml):
        code_tax = ''
        if aml.tax_line_id:
            code_tax = aml.tax_line_id.code_igv_dgi or ''
        else:
            for tax in aml.tax_ids:
                if tax.code_igv_dgi:
                    code_tax = tax.code_igv_dgi
        return code_tax