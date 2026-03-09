from odoo.exceptions import UserError, ValidationError
from odoo import fields

from .common import TestHrHospitalCommon

class TestHrHospitalVisit(TestHrHospitalCommon):

    def test_01_visit_archive_restriction(self):
        self.env['hr.hospital.visit'].create({
            'doctor_id': self.doctor.id,
            'patient_id': self.patient.id,
            'planned_date': fields.Datetime.now(),
            'visit_status': 'planned',
            'visit_type': 'initial'
        })
        with self.assertRaises(UserError):
            self.doctor.action_archive()

    def test_02_visit_weekend_not_allowed(self):
        with self.assertRaises(ValidationError):
            self.env['hr.hospital.visit'].create({
                'doctor_id': self.doctor.id,
                'patient_id': self.patient.id,
                'planned_date': "2026-03-08 13:00:00",
                'visit_status': 'planned',
                'visit_type': 'initial'
            })
