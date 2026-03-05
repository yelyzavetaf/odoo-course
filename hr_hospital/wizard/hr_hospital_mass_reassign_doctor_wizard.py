from odoo import models, fields, api
from odoo.exceptions import UserError


class HrHospitalMassReassignDoctorWizard(models.TransientModel):
    """
    Wizard for bulk reassigning patients from one doctor to another.

    Allows administrators to select a group of patients and update their
    attending doctor in one action. This process automatically triggers
    history logging and supports filtering patients by their current doctor.
    """
    _name = 'hr.hospital.mass.reassign.doctor.wizard'
    _description = 'Mass reassign doctor wizard'

    old_doctor_id = fields.Many2one(comodel_name='hr.hospital.doctor')
    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True
    )
    patient_ids = fields.Many2many(comodel_name='hr.hospital.patient')
    change_date = fields.Date(default=fields.Date.context_today, required=True)
    reason = fields.Text(required=True)

    @api.model
    def default_get(self, fields_list):
        """
        Pre-populate the patient list based on the user's current selection.

        If the wizard is launched from a list view (e.g., via Action menu),
        it automatically includes all selected patient IDs.

        :param list fields_list: Fields to retrieve default values for.
        :return: Dictionary of initial values.
        :rtype: dict
        """
        default_vals = super().default_get(fields_list)
        default_vals['patient_ids'] = [(
            6, 0, self.env.context.get('active_ids', [])
        )]
        return default_vals

    @api.onchange('old_doctor_id')
    def _onchange_old_doctor_id(self):
        """
        Dynamically filter the available patients based on the selected 'Old Doctor'.

        :return: A dictionary containing the domain for the patient_ids field.
        :rtype: dict
        """
        if self.old_doctor_id:
            return {'domain': {
                'patient_ids': [('doctor_id', '=', self.old_doctor_id.id)]}
            }
        return {'domain': {'patient_ids': []}}

    def action_reassign(self):
        """
        Execute the bulk update of attending doctors for the selected patients.

        Updates the 'doctor_id' field for all chosen patients. This will
        automatically trigger the 'write' method in the patient model to
        create history records.

        :raises UserError: If no patients are selected for reassignment.
        :return: Action to close the wizard.
        :rtype: dict
        """
        if not self.patient_ids:
            raise UserError("Please select patients.")

        self.patient_ids.write({
            'doctor_id': self.new_doctor_id.id
        })
