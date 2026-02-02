from odoo import models, fields


class HrHospitalVisit(models.Model):
    _name = 'hr.hospital.visit'
    _description = 'Visit'

    visit_date = fields.Datetime(
        string='Visit Scheduled Date',
        default=fields.Datetime.now
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

    diagnose_id = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diagnose',
    )
