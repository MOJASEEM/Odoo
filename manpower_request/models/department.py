from odoo import models, fields

class Department(models.Model):
    _name = 'manpower_request.department'
    _description = 'Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'department'

    department = fields.Char(string="Department Name")