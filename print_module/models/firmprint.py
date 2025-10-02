from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        self.ensure_one()  # Ensure the method is called on a single record
        report_action = self.env.ref('print_module.action_report_custom_invoice')
        return report_action.report_action(self)