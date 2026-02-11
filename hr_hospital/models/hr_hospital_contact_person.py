from odoo import models, fields


class HrHospitalContactPerson(models.Model):
    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'
    _inherit = 'hr.hospital.abstract.person'

    contact_patient_ids = fields.One2many(
        comodel_name='hr.hospital.patient',
        inverse_name='contact_id',
        string='Contact Person for Patients',
    )
