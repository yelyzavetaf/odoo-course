from datetime import date, timedelta
from odoo.tests.common import TransactionCase


class TestHrHospitalCommon(TransactionCase):

    def setUp(self):
        super(TestHrHospitalCommon, self).setUp()
        self.speciality = self.env['hr.hospital.doctor.speciality'].create({
            'name': 'Cardiologist',
            'speciality_code': 'CARD-01'
        })
        self.doctor = self.env['hr.hospital.doctor'].create({
            'first_name': 'Gregory',
            'last_name': 'House',
            'licence_number': 'DOC123',
            'licence_issued_date': date.today() - timedelta(days=3660), # 10 years ago
            'speciality_id': self.speciality.id,
            'phone_number': '1234567890',
            'birth_date': '1970-01-01'
        })

        self.patient = self.env['hr.hospital.patient'].create({
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': '1990-05-15',
            'blood_type': '0(i)+',
            'phone_number': '0987654321'
        })
