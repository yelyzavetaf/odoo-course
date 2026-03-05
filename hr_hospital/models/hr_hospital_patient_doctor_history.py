from datetime import datetime

from odoo import api, models, fields


class HrHospitalPatientDoctorHistory(models.Model):
    """
    Model for tracking the historical assignments of doctors to patients.

    This model maintains a chronological record of which doctor was assigned
    to a patient and when. It automatically manages record lifecycle by
    archiving previous assignments when a new doctor is designated.
    """
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

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to ensure only one doctor assignment is active at a time.

        Before creating new history records, it searches for existing active
        assignments for the same patients and marks them as inactive,
        setting the reassignment date to today.

        :param list vals_list: List of dictionaries containing record values.
        :return: Created records.
        :rtype: hr.hospital.patient.doctor.history
        """
        for vals in vals_list:
            patient_id = vals.get('patient_history_id')
            if patient_id:
                previous_history = self.search([
                    ('patient_history_id', '=', patient_id),
                    ('active', '=', True)
                ])
                if previous_history:
                    previous_history.write({
                        'active': False,
                        'reassigned_date': fields.Date.context_today(self),
                        'reassigned_reason': 'New doctor assignment'
                    })

        return super().create(vals_list)
