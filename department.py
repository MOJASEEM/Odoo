from odoo import models, fields ,api

class ManpowerRequestDepartment(models.Model):
    _name = 'manpower_request.department'
    _description = 'Department'
    _rec_name = 'dept_name'

    dept_name= fields.Char(string="Department",required=True)
