from odoo import models, fields ,api

class ManpowerRequestJob(models.Model):
    _name = 'manpower_request.job'
    _description = 'Job Position'
    _rec_name = 'job_name'

    job_name= fields.Char(string="Job Position",required=True)



