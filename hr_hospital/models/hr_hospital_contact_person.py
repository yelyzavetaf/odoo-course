from odoo import models, fields


class HrHospitalContactPerson(models.Model):
    """
    Model for storing information about contact persons related to patients.

    This model inherits from the abstract person model to provide common
    identity fields (name, phone, etc.) and establishes a relationship
    with patients who have specified allergies.
    """
    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'
    _inherit = 'hr.hospital.abstract.person'

    contact_patient_ids = fields.One2many(
        comodel_name='hr.hospital.patient',
        inverse_name='contact_id',
        string='Contact Person for Patients',
        domain="[('allergies', '!=', False), ('allergies', '!=', '')]",
    )
