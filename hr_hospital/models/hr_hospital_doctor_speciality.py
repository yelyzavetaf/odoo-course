from odoo import models, fields


class HrHospitalDoctorSpeciality(models.Model):
    _name = 'hr.hospital.doctor.speciality'
    _description = 'Doctor Speciality'
    _rec_name = 'name'

    active = fields.Boolean(default=True)

    name = fields.Char(required=True)
    speciality_code = fields.Char(size=10, required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)

    doctor_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='speciality_id',
        string='Doctors',
    )
