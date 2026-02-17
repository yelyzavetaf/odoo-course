import json
import io
import csv
import base64
from odoo import models, fields, api


class HrHospitalPatientCardExportWizard(models.TransientModel):
    _name = 'hr.hospital.patient.card.export.wizard'
    _description = 'Export meedical card'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True
    )
    date_start = fields.Date()
    date_end = fields.Date()

    include_diagnoses = fields.Boolean(default=True)
    include_recommendations = fields.Boolean(default=True)

    lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Report language',
    )
    export_format = fields.Selection([
        ('json', 'JSON'),
        ('csv', 'CSV')
    ], default='json', required=True)

    file_data = fields.Binary(string='File')
    file_name = fields.Char()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id and self._context.get('active_model') == 'hr.hospital.patient':
            patient = self.env['hr.hospital.patient'].browse(active_id)
            res['patient_id'] = patient.id

            if patient.language_id:
                lang = self.env['res.lang'].search(
                    domain=[('code', '=', patient.language_id)],
                    limit=1,
                )
                res['lang_id'] = lang.id
        return res

    def action_export(self):
        self.ensure_one()

        domain = [('patient_id', '=', self.patient_id.id)]
        if self.date_start:
            domain.append(('planned_date', '>=', self.date_start))
        if self.date_end:
            domain.append(('planned_date', '<=', self.date_end))

        visits = self.env['hr.hospital.visit'].search(domain)

        data_list = []
        for visit in visits:
            row = {
                'date': str(visit.planned_date),
                'doctor': visit.doctor_id.full_name,
            }
            if self.include_diagnoses:
                row['diagnosis'] = ", ".join(visit.diagnosis_ids.disease_id.mapped('name'))
            if self.include_recommendations:
                row['recommendations'] = visit.recommendations or ""
            data_list.append(row)

        if self.export_format == 'json':
            output = json.dumps(data_list, indent=4, ensure_ascii=False)
            file_content = base64.b64encode(output.encode('utf-8'))
            extension = 'json'
        else:
            output = io.StringIO()
            writer = csv.DictWriter(
                output, fieldnames=data_list[0].keys() if data_list else []
            )
            writer.writeheader()
            writer.writerows(data_list)
            file_content = base64.b64encode(output.getvalue().encode('utf-8'))
            extension = 'csv'

        self.write({
            'file_data': file_content,
            'file_name': f"patient_card_{self.patient_id.id}.{extension}"
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=file_data&filename={self.file_name}&download=true',
            'target': 'self',
        }
