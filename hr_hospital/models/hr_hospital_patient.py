from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'
    _inherit = 'hr.hospital.abstract.person'

    birth_date = fields.Date(required=True)

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Attending Doctor',
    )

    passport_data = fields.Char(size=10)

    contact_id = fields.Many2one(
        comodel_name='hr.hospital.contact.person',
        string='Contact Person',
    )

    blood_type = fields.Selection(
        selection=[
            ('0(i)+', 'O(I)+'),
            ('0(i)-', 'O(I)-'),
            ('a(ii)+', 'A(II)+'),
            ('a(ii)-', 'A(II)-'),
            ('b(iii)+', 'B(III)+'),
            ('b(iii)-', 'B(III)-'),
            ('ab(iv)+', 'AB(IV)+'),
            ('ab(iv)-', 'AB(IV)-')
        ],
        required=True)

    allergies = fields.Text()

    insurance_company_id = fields.Many2one(
        comodel_name='res.partner',
        string='Insurance Company',
        domain=[('is_company', '=', True)],
    )

    insurance_number = fields.Char()

    doctor_history_ids = fields.One2many(
        comodel_name='hr.hospital.patient.doctor.history',
        inverse_name='patient_history_id',
    )

    @api.constrains('birth_date')
    def _check_birth_date(self):
        for person in self:
            today = date.today()
            diff = relativedelta(today, person.birth_date)
            person.age = diff.years
            if person.age <= 0:
                raise ValidationError(
                    "Patient age can not be %s years." % person.age
                )

    @api.depends('full_name')
    def _compute_display_name(self):
        for patient in self:
            patient.display_name = patient.full_name

    def write(self, vals):
        if 'doctor_id' in vals:
            for patient in self:
                if patient.doctor_id.id != vals.get("doctor_id"):
                    self.env['hr.hospital.patient.doctor.history'].create({
                        'patient_id': patient.id,
                        'doctor_id': vals.get("doctor_id"),
                        'assigned_date': fields.Date.context_today(self),
                    })
        return super(HrHospitalPatient, self).write(vals)
