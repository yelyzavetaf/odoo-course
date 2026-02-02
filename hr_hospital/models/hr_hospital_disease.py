from odoo import models, fields


class HrHospitalDisease(models.Model):
    _name = 'hr.hospital.disease'
    _description = 'Disease'

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()

    is_contagious = fields.Boolean(default=False, string='Contagious')
