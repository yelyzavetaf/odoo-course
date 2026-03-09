from datetime import date, timedelta
from odoo.exceptions import ValidationError

from .common import TestHrHospitalCommon

class TestHrHospitalPatient(TestHrHospitalCommon):

    def test_01_patient_age_validation(self):
        with self.assertRaises(ValidationError):
            self.patient.write({'birth_date': date.today() + timedelta(days=1)})
