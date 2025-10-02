from odoo import models, fields

class Skills(models.Model):
    _name = 'man.skill'
    _description = 'Skills Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'skill'

    skill = fields.Char(string="Skill", required=True)
    request_id = fields.Many2one('man.model', string="Main Record",ondelete='cascade')


    #name = fields.Char(string="Department Name", required=True)
    #date_of_joining = fields.Date(string="Date of Joining")
    #notes = fields.Text(string="Notes")