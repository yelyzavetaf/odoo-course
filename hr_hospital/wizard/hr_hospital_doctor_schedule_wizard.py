from datetime import timedelta
from odoo import models, fields


class HrHospitalDoctorScheduleWizard(models.TransientModel):
    _name = 'hr.hospital.doctor.schedule.wizard'
    _description = 'Schedule fill in wizard'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True
    )
    start_date = fields.Date(
        string='Start date',
        required=True,
        default=fields.Date.today
    )
    weeks_count = fields.Integer(
        string='Number of weeks',
        default=1,
        required=True
    )

    schedule_type = fields.Selection([
        ('standard', 'Standard'),
        ('even', 'Even week'),
        ('odd', 'Odd week')
    ], default='standard', required=True)

    # Boolean поля для днів тижня
    mo = fields.Boolean('Monday')
    tu = fields.Boolean('Tuesday')
    we = fields.Boolean('Wednesday')
    th = fields.Boolean('Thursday')
    fr = fields.Boolean('Friday')
    sa = fields.Boolean('Saturday')
    su = fields.Boolean('Sunday')

    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)

    has_break = fields.Boolean()
    break_start = fields.Float()
    break_end = fields.Float()

    def action_generate_schedule(self):
        self.ensure_one()
        days_selection = {
            0: (self.mo, 'monday'),
            1: (self.tu, 'tuesday'),
            2: (self.we, 'wednesday'),
            3: (self.th, 'thursday'),
            4: (self.fr, 'friday'),
            5: (self.sa, 'saturday'),
            6: (self.su, 'sunday'),
        }

        schedule_vals = []
        for w in range(self.weeks_count):
            current_monday = self.start_date + timedelta(weeks=w)

            week_num = current_monday.isocalendar()[1]
            if self.schedule_type == 'even' and week_num % 2 != 0:
                continue
            if self.schedule_type == 'odd' and week_num % 2 == 0:
                continue

            for day_idx in range(7):
                is_selected, day_name = days_selection[day_idx]
                if is_selected:
                    work_date = current_monday + timedelta(days=day_idx)

                    if self.has_break and self.break_start > self.start_time and self.break_end < self.end_time:
                        schedule_vals.append(
                            self._prepare_schedule_val(work_date, day_name, self.start_time, self.break_start))

                        schedule_vals.append(
                            self._prepare_schedule_val(work_date, day_name, self.break_end, self.end_time))
                    else:
                        schedule_vals.append(
                            self._prepare_schedule_val(work_date, day_name, self.start_time, self.end_time))

        if schedule_vals:
            self.env['hr.hospital.doctor.schedule'].create(schedule_vals)

        return {'type': 'ir.actions.act_window_close'}

    def _prepare_schedule_val(self, date, day_name, start, end):
        return {
            'doctor_schedule_id': self.doctor_id.id,
            'date': date,
            'day_of_week': day_name,
            'start_time': start,
            'end_time': end,
            'type': 'work',
            'active': True,
        }
