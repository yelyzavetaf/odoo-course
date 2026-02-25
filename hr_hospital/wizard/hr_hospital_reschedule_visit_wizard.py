from odoo import models, fields, api
from odoo.exceptions import UserError


class HrHospitalRescheduleVisitWizard(models.TransientModel):
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
        res = super().default_get(fields_list)
        active_id = self._context.get('active_id')
        if active_id:
            res['visit_id'] = active_id
            visit = self.env['hr.hospital.visit'].browse(active_id)
            res['new_doctor_id'] = visit.doctor_id.id
        return res

    def action_reschedule(self):
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
