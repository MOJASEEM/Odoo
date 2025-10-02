from odoo import models, fields

class Qual(models.Model):
    _name = 'man.qual'
    _description = 'Qual Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'qual'

    qual = fields.Char(string="Educational Qualification")

