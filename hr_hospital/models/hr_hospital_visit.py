from odoo import models, fields


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Visit'

    active = fields.Boolean(default=True)

    visit_status = fields.Selection(
        selection=[
            ('planned', 'Planned'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
            ('missed', 'Missed by patient')
        ],
        required=True)

    planned_date = fields.Datetime(
        string='Visit Planned Date',
        default=fields.Datetime.now
    )

    actual_date = fields.Datetime(
        string='Visit Actual Date',
    )

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
    )

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True,
    )

    visit_type = fields.Selection(
        selection=[
            ('initial', 'Initial'),
            ('return', 'Return'),
            ('preventive', 'Preventive'),
            ('emergent', 'Emergent')
        ],
        required=True)

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default='base.USD',
        required=True,
    )

    visit_cost = fields.Monetary(
        currency_field='currency_id',
    )

    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.diagnosis',
        inverse_name='visit_id',
        string='Diagnosis',
    )

    recommendations = fields.Html()
