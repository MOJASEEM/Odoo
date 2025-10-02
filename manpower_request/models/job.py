from odoo import models, fields

class Job(models.Model):
    _name = 'man.job'
    _description = 'Job Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'job'

    job = fields.Char(string="Job position", required=True)
    #date_of_joining = fields.Date(string="Date of Joining")
    #notes = fields.Text(string="Notes")