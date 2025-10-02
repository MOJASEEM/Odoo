from odoo import models, fields

class ManpowerRequestQualification(models.Model):
    _name = 'manpower_request.qualification'
    _description = 'Qualification'
    _rec_name = 'quali_name'

    quali_name= fields.Char(string="Qualification",required=True)
