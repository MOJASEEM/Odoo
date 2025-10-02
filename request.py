from email.policy import default
import io
import base64
from openpyxl import Workbook
from openpyxl.styles import Border, Side
from openpyxl.utils import get_column_letter


from odoo import models, fields ,api

class ManpowerRequest(models.Model):
    _name = 'manpower_request.request'
    _description = 'Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    req_date = fields.Date(string="Request Date", required=True, default=fields.Date.context_today)
    req_seq = fields.Char("Sequence", readonly=True)
    dept=fields.Many2one("manpower_request.department",string="Department", required=True)
    job=fields.Many2one("manpower_request.job",string="Job Position",required=True)
    emp_num = fields.Integer(string="Number of Employees",required=True)
    quali = fields.Many2many("manpower_request.qualification", string="Qualification",required=True)
    exp = fields.Text(string="Experience")
    emp_type = fields.Selection(
        selection=[
            ('temporary', 'Temporary'),
            ('permanent', 'Permanent')
        ],
        string="Employment Type",
        default='temporary',
        required=True
    )
    skill = fields.Many2one('manpower_request.skill', string="Skill Type", ondelete='set null')
    skill_lines = fields.One2many(
        'manpower_request.skill.line',  # Target model
        'request_id',  # Related field in manpower_request.skill.line
        string="Skills"
    )

    state=fields.Selection([("draft","Draft"),("review","Review"),("approved","Approved"),("cancel","Cancelled")],default="draft",tracking=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get("req_seq", "New") == "New":  # Use req_seq instead of name
            vals["req_seq"] = self.env["ir.sequence"].next_by_code("manpower_request.sequence") or "New"
        return super(ManpowerRequest, self).create(vals)

    def action_download_excel(self):
        """Trigger the download of an Excel file for this specific record"""
        return self.env['report.manpower_request.manpower_excel_report'].get_xlsx_report(self.id)



    def action_edit(self):
        # Ensure one record is being processed
        self.ensure_one()

        # Return an action that simply opens the current record in form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'manpower_request.request',
            'view_mode': 'form',
            'view_id': self.env.ref('manpower_request.view_request_form_editable').id,
            'res_id': self.id,
            'target': 'current',
            'context': {'form_view_initial_mode': 'readonly'},
        }

    def action_save(self):
        """ Switch back to readonly form (auto-save) """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'manpower_request.request',
            'view_mode': 'form',
            'view_id': self.env.ref('manpower_request.view_request_form_readonly').id,
            'res_id': self.id,
            'target': 'current',
        }

    is_readonly = fields.Boolean(string="Readonly Mode", compute="_compute_is_readonly")

    @api.depends('state')
    def _compute_is_readonly(self):
        for record in self:
            record.is_readonly = record.state in ['approved', 'cancel']
            if record.is_readonly:
                record.action_edit()

    def action_print(self):
        return self.env.ref('manpower_request.action_report_request').report_action(self)

    def action_review(self):
        for rec in self:
            rec.state="review"
        self.ensure_one()

        # Return an action that simply opens the current record in form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'manpower_request.request',
            'view_mode': 'form',
            'view_id': self.env.ref('manpower_request.view_request_form_editable').id,
            'res_id': self.id,
            'target': 'current',
            'context': {'form_view_initial_mode': 'readonly'},
        }

    def action_confirm(self):
        for rec in self:
            rec.state="approved"
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'manpower_request.request',
            'view_mode': 'form',
            'view_id': self.env.ref('manpower_request.view_request_form_readonly').id,
            'res_id': self.id,
            'target': 'current',
        }

    def action_cancel(self):
        for rec in self:
            rec.state="cancel"
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'manpower_request.request',
            'view_mode': 'form',
            'view_id': self.env.ref('manpower_request.view_request_form_readonly').id,
            'res_id': self.id,
            'target': 'current',
        }

    def action_draft(self):
        for rec in self:
            rec.state="draft"
        self.ensure_one()

        # Return an action that simply opens the current record in form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'manpower_request.request',
            'view_mode': 'form',
            'view_id': self.env.ref('manpower_request.view_request_form_editable').id,
            'res_id': self.id,
            'target': 'current',
            'context': {'form_view_initial_mode': 'readonly'},
        }



class ManpowerRequestSkillLine(models.Model):
    _name = 'manpower_request.skill.line'
    _description = 'Manpower Request Skill Line'

    request_id = fields.Many2one('manpower_request.request', string="Manpower Request", ondelete='cascade')
    skill= fields.Many2one('manpower_request.skill', string="Skill", required=True)
    level = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),('4', '4'),
        ('5', '5')
    ], string="Level", required=True)