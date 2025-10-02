from odoo import fields, models, api

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        """Triggers the custom invoice report"""
        return self.env.ref('manpower_request.action_invoice_report').report_action(self)




