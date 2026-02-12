from odoo import models, fields


class HrHospitalDiagnosis(models.Model):
    _name = 'hr.hospital.diagnosis'
    _description = 'Diagnosis'

    active = fields.Boolean(default=True)

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.diagnosis',
        string='Visits',
        ondelete='cascade',
    )

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Diseases',
    )

    description = fields.Text()

    prescribed_treatment = fields.Html()

    approved = fields.Boolean(default=False)

    approved_by = fields.Many2one(
        comodel_name='hr.hospital.doctor',
    )

    approved_date = fields.Datetime()

    severity = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        required=True,
    )
