from odoo import models, fields


class HrHospitalPatient(models.Model):
    _name = 'hr.hospital.patient'
    _description = 'Patient'

    name = fields.Char()
    sex = fields.Selection(selection=[('female', 'Female'), ('male', 'Male')])

    complains = fields.Text()

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Attending Doctor',
    )
