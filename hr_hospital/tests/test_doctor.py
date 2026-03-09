from .common import TestHrHospitalCommon

class TestHrHospitalDoctor(TestHrHospitalCommon):

    def test_01_doctor_experience_calculation(self):
        self.doctor._compute_experience()
        doctor_experience = self.doctor.experience
        expected_experience = 10
        self.assertEqual(doctor_experience, expected_experience,
                         f"Expected experience {expected_experience}, got {doctor_experience}")

    def test_04_display_name_doctor(self):
        self.doctor._compute_display_name()
        expected_name = "House Gregory (Cardiologist)"
        self.assertEqual(self.doctor.display_name, expected_name)