from odoo import models, fields, api


class HrHospitalDiseaseReportWizard(models.TransientModel):
    """
    Wizard for generating analytical reports on diseases.

    Provides flexible filtering by doctors, specific diseases, and patient
    citizenship within a defined timeframe. Supports both detailed and
    summary report types with multiple grouping options for data analysis.
    """
    _name = 'hr.hospital.disease.report.wizard'
    _description = 'Disease Report'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors'
    )
    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diseases'
    )
    country_ids = fields.Many2many(
        comodel_name='res.country',
        string='Countries'
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    report_type = fields.Selection([
        ('detail', 'Detailed'),
        ('summary', 'Summary')
    ], default='detail', required=True)

    group_by = fields.Selection([
        ('doctor', 'Doctor'),
        ('disease', 'Disease'),
        ('month', 'Month'),
        ('country', 'Country')
    ], default='disease')

    @api.onchange('country_ids')
    def _onchange_country_ids(self):
        """
        Dynamically filter the available doctors based on selected countries.

        Filters doctors to show only those who received their education
        in the countries specified in the wizard.

        :return: A dictionary containing the domain for the doctor_ids field.
        :rtype: dict
        """
        domain = []
        if self.country_ids:
            domain = [('education_country_id', 'in', self.country_ids.ids)]

        return {'domain': {'doctor_ids': domain}}

    def action_get_report_data(self):
        """
        Construct a complex search domain and return the filtered diagnosis view.

        Aggregates filters from the wizard's fields (dates, doctors, diseases,
        and patient countries) to provide a precise subset of medical data.

        :return: A window action to display the filtered diagnoses.
        :rtype: dict
        """
        domain = [
            ('approved_date', '>=', self.date_start),
            ('approved_date', '<=', self.date_end)
        ]

        if self.doctor_ids:
            domain.append(
                ('visit_id.doctor_id', 'in', self.doctor_ids.ids)
            )

        if self.disease_ids:
            domain.append(
                ('disease_id', 'in', self.disease_ids.ids)
            )

        if self.country_ids:
            domain.append(
                ('visit_id.patient_id.country_id', 'in', self.country_ids.ids)
            )

        # diagnoses = self.env['hr.hospital.diagnosis'].search(domain)

        return {
            'name': 'Diagnooses report',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.diagnosis',
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }
