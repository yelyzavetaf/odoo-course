import re
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class HrHospitalAbstractPerson(models.AbstractModel):
    _name = 'hr.hospital.abstract.person'
    _description = 'Abstract Person'
    _inherit = 'image.mixin'

    active = fields.Boolean(default=True)

    last_name = fields.Char(required=True)
    first_name = fields.Char(required=True)
    middle_name = fields.Char()

    phone_number = fields.Char(required=True, size=10)
    email = fields.Char()

    sex = fields.Selection(selection=[
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other')
    ],
        default='other'
    )

    birth_date = fields.Date(required=True)

    age = fields.Integer(compute='_compute_age', readonly=True, store=True)

    full_name = fields.Char(compute='_compute_full_name', store=True)

    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Citizenship',
    )

    language_id = fields.Many2one(
        comodel_name='res.lang',
        string='Communication Language',
        default=lambda self: self.env.ref(
            'base.lang_en_GB', raise_if_not_found=False
        )
    )

    @api.constrains('phone_number')
    def _check_phone_number(self):
        for person in self:
            if person.phone_number and not person.phone_number.isdigit():
                raise ValidationError(
                    "Phone number should contain digits only."
                )
            if person.phone_number and len(person.phone_number) < 10:
                raise ValidationError("Phone number is too short.")

    @api.constrains('email')
    def _check_email(self):
        for person in self:
            if person.email:
                email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                if not re.match(email_regex, person.email):
                    raise ValidationError(
                        ("Wrong email format: %s") % person.email
                    )

    @api.depends('birth_date')
    def _compute_age(self):
        for person in self:
            today = date.today()
            diff = relativedelta(today, person.birth_date)
            person.age = diff.years

    @api.depends('last_name', 'first_name', 'middle_name')
    def _compute_full_name(self):
        for person in self:
            last_name = person.last_name or ''
            first_name = person.first_name or ''
            middle_name = person.middle_name or ''
            person.full_name = (
                f"{last_name} {first_name} {middle_name}".strip())
