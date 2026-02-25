from datetime import datetime, time

from odoo import api, models, fields

from odoo.exceptions import UserError, ValidationError


class HrHospitalVisit(models.Model):
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
        for record in self:
            if not record.planned_date or not record.doctor_id:
                continue

            weekday = record.planned_date.weekday()
            if weekday >= 5:
                raise ValidationError(
                    "Scheduling a visit for a weekend is not allowed."
                )

            visit_date = record.planned_date.date()
            holiday = self.env['hr.hospital.doctor.schedule'].search([
                ('doctor_schedule_id', '=', record.doctor_id.id),
                ('date', '=', visit_date),
                ('type', '=', 'vacation'),
                ('active', '=', True)
            ], limit=1)

            if holiday:
                raise ValidationError(
                    f"Doctor {record.doctor_id.full_name} on "
                    f"{visit_date} is on vacation!"
                )

    @api.depends('patient_id', 'doctor_id')
    def _compute_display_name(self):
        for visit in self:
            visit.display_name = (f"{visit.patient_id.full_name} "
                                  f"({visit.doctor_id.full_name} "
                                  f"({visit.doctor_id.speciality_id.name}))")

    @api.depends('diagnosis_ids')
    def _compute_diagnosis_count(self):
        for visit in self:
            visit.diagnosis_count = len(visit.diagnosis_ids)

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id and self.patient_id.allergies:
            return {
                'warning': {
                    'title': "Warning",
                    'message': f"The chosen patient has allergies "
                               f"{self.patient_id.allergies}."
                }
            }

    @api.model_create_multi
    def create(self, vals_list):
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
                    raise UserError(
                        f"Patient has already planned a visit to "
                        f"{doctor.display_name} for {planned_dt.date()}."
                    )
        return super().create(vals_list)

    def write(self, vals):
        essential_fields = [
            'doctor_id', 'patient_id', 'planned_date', 'actual_date'
        ]
        for visit in self:
            if visit.actual_date:
                if visit.actual_date.date() < fields.Date.context_today(self):
                    if any(field in vals for field in essential_fields):
                        raise UserError(
                            f"Updating past visit (ID: {visit.id}) "
                            f"is not allowed."
                        )
        return super().write(vals)

    def unlink(self):
        for visit in self:
            if visit.diagnosis_ids:
                raise UserError(
                    f"Removing visit (ID: {visit.id}) is not allowed "
                    "because of diagnosis added."
                )
        return super().unlink()
