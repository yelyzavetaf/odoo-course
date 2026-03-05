from datetime import datetime, time

from odoo import _, api, models, fields

from odoo.exceptions import UserError, ValidationError


class HrHospitalVisit(models.Model):
    """
    Model for managing patient appointments and medical consultations.

    Tracks the lifecycle of a visit from planning to completion or cancellation.
    Stores clinical data such as visit type, actual timing, associated
    diagnoses, and financial information using the company's default currency.
    """
    _name = 'hr.hospital.visit'
    _description = 'Visit'

    active = fields.Boolean(default=True)

    visit_status = fields.Selection(
        selection=[
            ('planned', 'Planned'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
            ('missed', 'Missed by patient')
        ],
        required=True)

    planned_date = fields.Datetime(
        string='Visit Planned Date',
        default=fields.Datetime.now
    )

    actual_date = fields.Datetime(
        string='Visit Actual Date',
    )

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
        domain=[('licence_number', '!=', False)],
    )

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True,
    )

    visit_type = fields.Selection(
        selection=[
            ('initial', 'Initial'),
            ('return', 'Return'),
            ('preventive', 'Preventive'),
            ('emergent', 'Emergent')
        ],
        required=True)

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    visit_cost = fields.Monetary(
        currency_field='currency_id',
    )

    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.diagnosis',
        inverse_name='visit_id',
    )

    diagnosis_count = fields.Integer(
        string='Number of Diagnoses',
        compute='_compute_diagnosis_count',
        store=True
    )

    recommendations = fields.Html(
        sanitize="True",
    )

    @api.constrains('planned_date', 'doctor_id')
    def _check_visit_date_validity(self):
        """
        Ensure the visit date is valid according to hospital policy and doctor availability.

        Validates that:
        - The visit is not scheduled on a weekend (Saturday or Sunday).
        - The assigned doctor is not on vacation for the selected date.

        :raises ValidationError: If the date falls on a weekend or conflicts with doctor's vacation.
        """
        for record in self:
            if not record.planned_date or not record.doctor_id:
                continue

            weekday = record.planned_date.weekday()
            if weekday >= 5:
                raise ValidationError(
                    _("Scheduling a visit for a weekend is not allowed.")
                )

            visit_date = record.planned_date.date()
            holiday = self.env['hr.hospital.doctor.schedule'].search([
                ('doctor_schedule_id', '=', record.doctor_id.id),
                ('date', '=', visit_date),
                ('type', '=', 'vacation'),
                ('active', '=', True)
            ], limit=1)

            if holiday:
                raise ValidationError(_(
                    f"Doctor {record.doctor_id.full_name} on "
                    f"{visit_date} is on vacation!"
                ))

    @api.depends('patient_id', 'doctor_id')
    def _compute_display_name(self):
        """
        Generate a descriptive display name for the visit.
        Format: "Patient Name (Doctor Name (Specialty))"
        """
        for visit in self:
            visit.display_name = (f"{visit.patient_id.full_name} "
                                  f"({visit.doctor_id.full_name} "
                                  f"({visit.doctor_id.speciality_id.name}))")

    @api.depends('diagnosis_ids')
    def _compute_diagnosis_count(self):
        """
        Calculate the total number of diagnoses associated with this visit.
        """
        for visit in self:
            visit.diagnosis_count = len(visit.diagnosis_ids)

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """
        Display a warning notification if the selected patient has documented allergies.
        """
        if self.patient_id and self.patient_id.allergies:
            return {
                'warning': {
                    'title': _("Warning"),
                    'message': _(f"The chosen patient has allergies "
                                 f"{self.patient_id.allergies}.")
                }
            }

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to prevent duplicate appointments on the same day.

        Checks if a patient already has an active visit scheduled with the
        same doctor on the same calendar date.

        :raises UserError: If a duplicate visit is detected.
        """
        for vals in vals_list:
            patient_id = vals.get('patient_id')
            doctor_id = vals.get('doctor_id')
            planned_dt_str = vals.get('planned_date')

            if patient_id and doctor_id and planned_dt_str:
                planned_dt = fields.Datetime.to_datetime(planned_dt_str)

                start_of_day = datetime.combine(planned_dt.date(), time.min)
                end_of_day = datetime.combine(planned_dt.date(), time.max)

                duplicate = self.search([
                    ('patient_id', '=', patient_id),
                    ('doctor_id', '=', doctor_id),
                    ('active', '=', True),
                    ('planned_date', '>=', start_of_day),
                    ('planned_date', '<=', end_of_day),
                ], limit=1)

                if duplicate:
                    doctor = self.env['hr.hospital.doctor'].browse(doctor_id)
                    raise UserError(_(
                        f"Patient has already planned a visit to "
                        f"{doctor.display_name} for {planned_dt.date()}."
                    ))
        return super().create(vals_list)

    def write(self, vals):
        """
        Restrict modifications to historical visit records.

        Prevents changing essential fields (doctor, patient, dates) if the
        visit's actual date is in the past, ensuring data integrity.

        :raises UserError: If an attempt is made to update a past visit.
        """
        essential_fields = [
            'doctor_id', 'patient_id', 'planned_date', 'actual_date'
        ]
        for visit in self:
            if visit.actual_date:
                if visit.actual_date.date() < fields.Date.context_today(self):
                    if any(field in vals for field in essential_fields):
                        raise UserError(_(
                            f"Updating past visit (ID: {visit.id}) "
                            f"is not allowed."
                        ))
        return super().write(vals)

    def unlink(self):
        """
        Prevent deletion of visits that contain medical findings.

        Ensures that any visit with linked diagnoses cannot be removed
        from the system to preserve medical history.

        :raises UserError: If the visit has one or more associated diagnoses.
        """
        for visit in self:
            if visit.diagnosis_ids:
                raise UserError(_(
                    f"Removing visit (ID: {visit.id}) is not allowed "
                    "because of diagnosis added."
                ))
        return super().unlink()
