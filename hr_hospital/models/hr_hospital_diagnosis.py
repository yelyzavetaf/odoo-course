from datetime import timedelta

from odoo import api, models, fields


class HrHospitalDiagnosis(models.Model):
    _name = 'hr.hospital.diagnosis'
    _description = 'Diagnosis'

    active = fields.Boolean(default=True)

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='Visits',
        ondelete='cascade',
        domain=lambda self: self._get_visit_domain(),
    )

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Diseases',
        domain=[
            ('is_contagious', '=', True),
            ('severity', 'in', ['high', 'critical'])
        ]
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

    @api.model
    def _get_visit_domain(self):
        date_limit = fields.Date.today() - timedelta(days=30)
        return [
            ('state', '=', 'done'),
            ('actual_date', '>=', date_limit)
        ]
