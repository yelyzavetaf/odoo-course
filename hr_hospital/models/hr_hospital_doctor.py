from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields

from odoo.exceptions import UserError, ValidationError


class HrHospitalDoctor(models.Model):
    _name = 'hr.hospital.doctor'
    _description = 'Doctor'
    _inherit = 'hr.hospital.abstract.person'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='System User',
        ondelete='restrict',
    )

    speciality_id = fields.Many2one(
        comodel_name='hr.hospital.doctor.speciality',
        string='Speciality',
        required=True,
    )

    is_intern = fields.Boolean(default=False)

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Mentor',
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

    @api.constrains('rating')
    def _check_rating_range(self):
        for rec in self:
            if rec.rating < 0.00 or rec.rating > 5.00:
                raise ValidationError("Rating should be from 0.00 to 5.00!")

    @api.depends('full_name')
    def _compute_display_name(self):
        for doctor in self:
            doctor.display_name = (
                '%s (%s)' % (doctor.full_name, doctor.speciality_id.name)
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

    def write(self, vals):
        if 'active' in vals and not vals.get('active'):
            for doctor in self:
                if doctor.visits_ids:
                    for visit in doctor.visits_ids:
                        if visit.active:
                            raise UserError(
                                "Can not archive doctor with active visits."
                            )
        return super(HrHospitalDoctor, self).write(vals)
