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

    def _compute_visit_count(self):
        for patient in self:
            patient.visit_count = self.env['hr.hospital.visit'].search_count([
                ('patient_id', '=', patient.id)
            ])

    def action_view_patient_visits(self):
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

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:

            country_code = self.country_id.code
            lang = self.env['res.lang'].search([
                ('code', 'ilike', country_code)
            ], limit=1)

            if lang:
                self.language_id = lang
                return {
                    'warning': {
                        'title': "Patient country was changed",
                        'message': "Suggested language was updated "
                                   "to %s" % lang.display_name,
                    }
                }

    def write(self, vals):
        if 'doctor_id' in vals:
            for patient in self:
                if patient.doctor_id.id != vals.get("doctor_id"):
                    self.env['hr.hospital.patient.doctor.history'].create({
                        'patient_history_id': patient.id,
                        'doctor_history_id': vals.get("doctor_id"),
                        'assigned_date': fields.Date.context_today(self),
                    })
        return super(HrHospitalPatient, self).write(vals)
