from datetime import datetime

from odoo import models, fields


class HrHospitalPatientDoctorHistory(models.Model):
    _name = 'hr.hospital.patient.doctor.history'
    _description = 'Patient Doctor History'

    active = fields.Boolean(default=True)

    doctor_history_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
    )

    patient_history_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True,
    )

    assigned_date = fields.Date(required=True, default=datetime.today())

    reassigned_date = fields.Date()

    reassigned_reason = fields.Text()
