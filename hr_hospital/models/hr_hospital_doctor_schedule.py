from datetime import datetime

from odoo import models, fields


class HrHospitalDoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'

    active = fields.Boolean(default=True)

    doctor_schedule_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
    )

    day_of_week = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ])

    date = fields.Date(default=datetime.today())

    start_time = fields.Float(
        help="Format: 8:30 = 8.5"
    )

    end_time = fields.Float()

    type = fields.Selection([
        ('work', 'Work day'),
        ('vacation', 'Vacation'),
        ('sick', 'Sick leave'),
        ('conference', 'Conference'),
    ])

    notes = fields.Char()

    _check_start_end_time = models.Constraint(
        'CHECK(start_time < end_time)',
        'Schedule start time should earlier than end time.'
    )
