from odoo import models, fields

class ManpowerRequestSkills(models.Model):
    _name = 'manpower_request.skill'
    _description = 'Skills'
    _rec_name = 'skill_name'

    skill_name= fields.Char(string="Skill Type",required=True)