from odoo import models, fields, api
from odoo.exceptions import UserError


class HrHospitalMassReassignDoctorWizard(models.TransientModel):
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
        default_vals = super().default_get(fields_list)
        default_vals['patient_ids'] = [(
            6, 0, self.env.context.get('active_ids', [])
        )]
        return default_vals

    @api.onchange('old_doctor_id')
    def _onchange_old_doctor_id(self):
        if self.old_doctor_id:
            return {'domain': {
                'patient_ids': [('doctor_id', '=', self.old_doctor_id.id)]}
            }
        return {'domain': {'patient_ids': []}}

    def action_reassign(self):
        if not self.patient_ids:
            raise UserError("Please select patients.")

        self.patient_ids.write({
            'doctor_id': self.new_doctor_id.id
        })
