from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields

from odoo.exceptions import UserError, ValidationError


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'
    _inherit = 'hr.hospital.abstract.person'
    _rec_names_search = 'full_name'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='System User',
        ondelete='restrict',
    )

    speciality_id = fields.Many2one(
        comodel_name='hr.hospital.doctor.speciality',
        required=True,
    )

    is_intern = fields.Boolean(default=False)

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        domain=[('is_intern', '=', False)],
    )

    intern_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='mentor_id',
        string='Interns'
    )

    patient_ids = fields.One2many(
        comodel_name='hr.hospital.patient',
        inverse_name='doctor_id',
        string='Patients',
    )

    licence_number = fields.Char(required=True, copy=False)

    licence_issued_date = fields.Date(required=True)

    experience = fields.Integer(
        compute='_compute_experience',
        string="Years of experience",
        readonly=True,
    )

    education_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country of Education',
    )

    work_schedule_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.schedule',
        inverse_name='doctor_schedule_id',
    )

    patient_history_ids = fields.One2many(
        comodel_name='hr.hospital.patient.doctor.history',
        inverse_name='doctor_history_id',
    )

    rating = fields.Float(
        digits=(3, 2),
        default=3.00
    )

    visits_ids = fields.One2many(
        comodel_name='hr.hospital.visit',
        inverse_name='doctor_id',
    )

    _licence_number_unique = models.Constraint(
        'unique(licence_number)',
        'Doctor should have a unique licence number.'
    )

    _check_rating_range = models.Constraint(
        'CHECK(rating <= 5.0 AND rating >= 0.0)',
        'Doctor rating should be from 0.00 to 5.00'
    )

    @api.depends('full_name')
    def _compute_display_name(self):
        for doctor in self:
            doctor.display_name = (
                f"{doctor.full_name} ({doctor.speciality_id.name})"
            )

    @api.depends('experience')
    def _compute_experience(self):
        for doctor in self:
            today = date.today()
            diff = relativedelta(today, doctor.licence_issued_date)
            doctor.experience = diff.years

    @api.constrains('mentor_id')
    def _check_self_mentor(self):
        for doctor in self:
            if doctor.mentor_id == self.user_id:
                raise ValidationError("Doctor can not be his/her own mentor.")
            if doctor.mentor_id.is_intern:
                raise ValidationError("Intern can not be a mentor.")

    @api.onchange('is_intern')
    def _onchange_is_intern(self):
        if self.is_intern:
            self.mentor_id = self.env['hr.hospital.doctor'].browse(2)
            return {
                'warning': {
                    'title': "Intern was chosen",
                    'message': "Mentor was assigned automatically",
                }
            }

    def action_archive(self):
        for doctor in self:
            if doctor.visits_ids:
                for visit in doctor.visits_ids:
                    if visit.active:
                        raise UserError(
                            "Can not archive doctor with active visits."
                        )
        return super().action_archive()

    def action_create_visit_from_kanban(self):
        self.ensure_one()
        return {
            'name': 'New Visit',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_doctor_id': self.id,
                'default_planned_date': fields.Datetime.now(),
            },
        }
