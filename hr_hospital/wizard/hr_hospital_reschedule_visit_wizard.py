from odoo import models, fields, api
from odoo.exceptions import UserError


class HrHospitalRescheduleVisitWizard(models.TransientModel):
    """
    Wizard for rescheduling patient appointments.

    Facilitates the process of moving an existing visit to a new date or
    assigning a different doctor. The original visit is archived,
    and a new record is created to maintain full traceability of changes.
    """
    _name = 'hr.hospital.reschedule.visit.wizard'
    _description = 'Reschedule Visit'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='Current visit', readonly=True
    )
    new_doctor_id = fields.Many2one(comodel_name='hr.hospital.doctor')
    new_date = fields.Datetime(required=True)
    reason = fields.Text(required=True)

    @api.model
    def default_get(self, fields_list):
        """
        Pre-populate the wizard with data from the source visit record.

        Automatically links the active visit and suggests the current doctor
        as a default for the new appointment.

        :param list fields_list: Fields to retrieve default values for.
        :return: Initial values dictionary.
        :rtype: dict
        """
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['visit_id'] = active_id
            visit = self.env['hr.hospital.visit'].browse(active_id)
            res['new_doctor_id'] = visit.doctor_id.id
        return res

    def action_reschedule(self):
        """
        Archive the current visit and create a new one with updated details.

        Sets the current visit to inactive and initializes a new visit record
        copying essential data (patient, type) but applying the new timing.

        :raises UserError: If the source visit cannot be identified.
        :return: An action to open the newly created visit form.
        :rtype: dict
        """
        self.ensure_one()
        if not self.visit_id:
            raise UserError("Visit not found.")

        self.visit_id.write({
            'active': False,
        })

        new_visit = self.env['hr.hospital.visit'].create({
            'patient_id': self.visit_id.patient_id.id,
            'doctor_id': self.new_doctor_id.id or self.visit_id.doctor_id.id,
            'planned_date': self.new_date,
            'visit_status': 'plaanned',
            'visit_type': self.visit_id.visit_type,
        })

        return {
            'name': 'New visit',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'res_id': new_visit.id,
            'view_mode': 'form',
            'target': 'current',
        }
