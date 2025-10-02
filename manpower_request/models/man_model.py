import io
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import xlsxwriter
from reportlab.pdfgen import canvas
from odoo.http import content_disposition
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64


class ManModel(models.Model):
    _name = 'man.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Man Power Request'
    name = fields.Char(string="Name", required=True)
    department = fields.Many2one('manpower_request.department')  # Fixed model name
    job= fields.Many2one('man.job', string="Job Position")
    no_of_employee = fields.Integer(string="No. of Employees")
    job_position = fields.Char(string="Job Position")
    experience = fields.Integer(string="Experience")
    #header = fields.Char(string="Header")
    #body= fields.Text(string="Body")
    #footer = fields.Char(string="Footer")
    pdf_report = fields.Binary("PDF Report", readonly=True)
    pdf_report_name = fields.Char("PDF File Name",readonly=True)

    qual = fields.Many2many('man.qual',string="Educational Qualification")
    #skill = fields.Many2one('man.skill', string="Skill Type")
    skill = fields.Many2one(
        'man.skill',
        string="Skill")
    skill_line = fields.One2many('man.skill.line', 'request_id', string="Skill Line")

    employee_type = fields.Selection(
        [('permanent', 'Permanent'), ('contract', 'Contract')],
        string="Employee Type",
        help="Specify whether the employee is Permanent or Contract-based"
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string="State", default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("man.model") or "New"
        return super(ManModel, self).create(vals)

    excel_file = fields.Binary(string="Excel File")
    file_name = fields.Char(string="File Name")

    def action_download_pdf(self):

        for record in self:
            # Create an in-memory buffer for the PDF
            buffer = BytesIO()

            # Create the PDF document
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []

            # Title
            title = f"Man Model Report: {record.name or 'N/A'}"
            elements.append(Table([[title]], style=[
                ('BACKGROUND', (0, 0), (-1, -1), colors.skyblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14)
            ]))
            elements.append(Table([[" "]]))  # Add some space

            # Add general details in a table format
            data = [
                ['Department', record.department.department if record.department else 'N/A'],
                ['Number of Employees', record.no_of_employee or 'N/A'],
                ['Job', record.job.job if record.job else 'N/A'],
                #['Job Position', record.job_position.job if record.job_position else 'N/A'],
                ['Experience', record.experience or 'N/A'],
                ['Qualifications', ', '.join(record.qual.mapped('qual')) if record.qual else 'N/A'],
                ['Employee Type',
                 dict(record.fields_get('employee_type')['employee_type'].get('selection', {})).get(
                     record.employee_type,
                     'N/A')],
            ]
            table = Table(data, colWidths=[150, 400])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.skyblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)

            elements.append(Table([[" "]]))  # Add some space

            # Add Skills (one2many field: skill_line)
            if record.skill_line:
                elements.append(Table([["Skills"]], style=[
                    ('BACKGROUND', (0, 0), (-1, -1), colors.skyblue),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                ]))
                skill_data = [['Skill Name', 'Level']]  # Header row
                for line in record.skill_line:
                    skill_data.append([
                        line.skill_id.skill if line.skill_id else 'N/A',
                        line.level or 'N/A'
                    ])
                skill_table = Table(skill_data, colWidths=[200, 200])
                skill_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ]))
                elements.append(skill_table)

            # Build the PDF
            doc.build(elements)

            # Get the PDF content from the buffer
            pdf_data = buffer.getvalue()
            buffer.close()

            # Encode the PDF into base64 format and update the record fields
            record.write({
                'pdf_report': base64.b64encode(pdf_data),
                'pdf_report_name': f"Man_Model_Report_{record.id}.pdf",
            })

            # Return an action to download the file
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{record._name}/{record.id}/pdf_report/{record.pdf_report_name}?download=true',
                'target': 'self',
            }

    def action_export_excel(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Manpower Data')

        # Define headers
        headers = ['Sequence number','Department', 'Job Position', 'Experience', 'No. of Employees', 'Qualification', 'Skill']

        # Formatting
        title_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 14})
        header_format = workbook.add_format({'bg_color': '#D3D3D3', 'border': 1, 'bold': True})
        sheet.set_column(0, len(headers) - 1, 20)

        # Merge header title
        sheet.merge_range('A1:F1', 'Manpower Request Form', title_format)

        # Write headers in row 2 (index 1)
        for col, header in enumerate(headers):
            sheet.write(1, col, header, header_format)

        # Write data starting from row 3 (index 2)
        row = 2
        for record in self:
            qualifications = ", ".join(record.qual.mapped('qual')) if record.qual else "No Qualification"
            skills = ", ".join(record.skill_line.mapped('skill_id.skill')) if record.skill_line else "No Skills"
            sheet.write(row, 0, record.name)
            sheet.write(row, 1, record.department.department if record.department else 'No Department')
            sheet.write(row, 2, record.job.job if record.job else 'No Job')
            sheet.write(row, 3, record.experience)
            sheet.write(row, 4, record.no_of_employee)
            sheet.write(row, 5, qualifications)
            sheet.write(row, 6, skills)
            row += 1  # Move to the next row

        workbook.close()
        output.seek(0)

        # Save file
        file_data = base64.b64encode(output.getvalue())
        output.close()
        self.write({
            'excel_file': file_data,
            'file_name': f"Manpower_Request_{self.id}.xlsx"
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content?model=man.model&id={self.id}&field=excel_file&filename_field=file_name&download=true",
            'target': 'self',
        }

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    def action_ongoing(self):
        for record in self:
            record.state = 'ongoing'
    def action_done(self):
        for record in self:
            record.state = 'done'
    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_reset_draft(self):
        for record in self:
            record.state = 'draft'

class ManpowerRequestSkillLine(models.Model):
    _name = 'man.skill.line'
    #_description = 'Manpower Request Skill Line'

    request_id = fields.Many2one('man.model', string="Manpower Request", ondelete='cascade')
    skill_id= fields.Many2one('man.skill', string="Skill", required=True)
    level = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')
    ], string="Level",required=True)



