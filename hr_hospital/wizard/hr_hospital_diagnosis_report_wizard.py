from odoo import models, fields, api


class DiagnosisReportWizard(models.TransientModel):
    _name = 'hr.hospital.diagnosis.report.wizard'
    _description = 'Diagnosis report wizard'

    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)

    doctor_ids = fields.Many2many('hr.hospital.doctor', string='Doctors')
    disease_ids = fields.Many2many('hr.hospital.disease', string='Diseases')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_model == 'hr.hospital.doctor' and active_ids:
            res['doctor_ids'] = [(6, 0, active_ids)]

        return res

    def action_open_report(self):
        self.ensure_one()
        domain = [
            ('approved_date', '>=', self.date_from),
            ('approved_date', '<=', self.date_to)
        ]

        if self.doctor_ids:
            domain.append(('approved_by', 'in', self.doctor_ids.ids))
        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))

        return {
            'name': f'Diagnoses report ({self.date_from} - {self.date_to})',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.diagnosis',
            'view_mode': 'list,pivot,graph',
            'domain': domain,
            'context': {
                'search_default_group_by_disease': 1,
                'expand': 1
            },
            'target': 'current',
        }
