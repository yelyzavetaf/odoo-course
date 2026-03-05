from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


class HrHospitalPatient(models.Model):
    """
    Model for managing patient records within the hospital ecosystem.

    Extends the abstract person model to include specific medical data such
    as blood type, allergies, and birthdate. It maintains relationships
    with attending doctors, insurance companies, and contact persons.
    The model also tracks clinical history through automated visit counting
    and diagnosis logs.
    """
    _name = 'hr.hospital.patient'
    _description = 'Patient'
    _inherit = 'hr.hospital.abstract.person'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Patient User',
        ondelete='restrict',
    )

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
        domain=[('is_company', '=', True)],
    )

    insurance_number = fields.Char()

    doctor_history_ids = fields.One2many(
        comodel_name='hr.hospital.patient.doctor.history',
        inverse_name='patient_history_id',
        context={'active_test': False},
    )

    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.diagnosis',
        inverse_name='patient_id',
        string='Diagnoses history',
        readonly=True
    )

    visit_count = fields.Integer(
        compute='_compute_visit_count',
        string='Number of visits',
    )

    last_visit_id = fields.Many2one(
        comodel_name='hr.hospital.visit',
        string='last_visit',
        compute='_compute_last_visit_id',
        store=True
    )

    def _compute_last_visit_id(self):
        """
        Identify and store the most recent visit for each patient.

        Searches the visit records ordered by planned date in descending order
        to find the single latest occurrence.
        """
        for patient in self:
            last_visit = self.env['hr.hospital.visit'].search([
                ('patient_id', '=', patient.id),
            ], order='planned_date desc', limit=1)

            patient.last_visit_id = last_visit

    def _compute_visit_count(self):
        """
        Calculate the total number of visits associated with the patient.

        Used for displaying statistics in the stat-button on the patient form.
        """
        for patient in self:
            patient.visit_count = self.env['hr.hospital.visit'].search_count([
                ('patient_id', '=', patient.id)
            ])

    def action_view_patient_visits(self):
        """
        Return an action to display a filtered list of all visits for this patient.

        Provides multiple view modes (list, form, calendar) and sets the
        default patient in the context for new records.
        """
        self.ensure_one()
        return {
            'name': 'Patient visits',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'list,form,calendar',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    def action_create_new_visit(self):
        """
        Launch a wizard-style modal form to create a new visit for the patient.

        Automatically pre-fills the patient field and sets the planned date to now.
        """
        self.ensure_one()
        return {
            'name': 'New visit',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.id,
                'default_planned_date': fields.Datetime.now(),
            },
        }

    @api.constrains('birth_date')
    def _check_birth_date(self):
        """
        Validate the patient's birthdate and calculate their age.

        Ensures that the birthdate is in the past and the calculated age
        is a positive integer.

        :raises ValidationError: If the calculated age is zero or negative.
        """
        for person in self:
            today = date.today()
            diff = relativedelta(today, person.birth_date)
            person.age = diff.years
            if person.age <= 0:
                raise ValidationError(
                    _(f"Patient age can not be {person.age} years.")
                )

    @api.depends('full_name')
    def _compute_display_name(self):
        """
        Set the record's display name to the patient's full name.
        """
        for patient in self:
            patient.display_name = patient.full_name

    @api.onchange('country_id')
    def _onchange_country_id(self):
        """
        Automatically suggest a language based on the selected country's code.

        Searches for a matching language record and provides a warning
        notification to the user about the suggested update.
        """
        if self.country_id:

            country_code = self.country_id.code
            lang = self.env['res.lang'].search([
                ('code', 'ilike', country_code)
            ], limit=1)

            if lang:
                self.language_id = lang
                return {
                    'warning': {
                        'title': _("Patient country was changed"),
                        'message': _(f"Suggested language was updated "
                                     f"to {lang.display_name}")
                    }
                }

    def write(self, vals):
        """
        Override write to track changes in the attending doctor.

        Whenever the doctor_id is updated, a new entry is created in the
        patient's doctor history to maintain a chronological record of assignments.
        """
        if 'doctor_id' in vals:
            for patient in self:
                if patient.doctor_id.id != vals.get("doctor_id"):
                    self.env['hr.hospital.patient.doctor.history'].create({
                        'patient_history_id': patient.id,
                        'doctor_history_id': vals.get("doctor_id"),
                        'assigned_date': fields.Date.context_today(self),
                    })
        return super().write(vals)
