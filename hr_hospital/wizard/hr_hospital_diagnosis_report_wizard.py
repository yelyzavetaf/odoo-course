from odoo import models, fields, api


class DiagnosisReportWizard(models.TransientModel):
    """
    Wizard for generating filtered reports of approved diagnoses.

    Allows users to define a specific date range and filter results by
    medical professionals or specific diseases. The results are presented
    through dynamic views including lists, pivot tables, and graphs.
    """
    _name = 'hr.hospital.diagnosis.report.wizard'
    _description = 'Diagnosis report wizard'

    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)

    doctor_ids = fields.Many2many('hr.hospital.doctor', string='Doctors')
    disease_ids = fields.Many2many('hr.hospital.disease', string='Diseases')

    @api.model
    def default_get(self, fields_list):
        """
        Pre-fill the doctor selection based on the active UI context.

        If the wizard is launched from a doctor's record or list,
        automatically adds those doctors to the wizard's selection.

        :param list fields_list: Fields to get default values for.
        :return: Dictionary of default values.
        :rtype: dict
        """
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_model == 'hr.hospital.doctor' and active_ids:
            res['doctor_ids'] = [(6, 0, active_ids)]

        return res

    def action_open_report(self):
        """
        Execute the search and open the diagnosis view with applied filters.

        Constructs a dynamic domain based on the user's input and returns
        an action to display the matching diagnosis records.

        :return: Dictionary defining the client-side window action.
        :rtype: dict
        """
        self.ensure_one()
        domain = [
            ('approved_date', '>=', self.date_from),
            ('approved_date', '<=', self.date_to)
        ]

        if self.doctor_ids:
            domain.append(('approved_by', 'in', self.doctor_ids.ids))
        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))

        return {
            'name': f'Diagnoses report ({self.date_from} - {self.date_to})',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.diagnosis',
            'view_mode': 'list,pivot,graph',
            'domain': domain,
            'context': {
                'search_default_group_by_disease': 1,
                'expand': 1
            },
            'target': 'current',
        }
