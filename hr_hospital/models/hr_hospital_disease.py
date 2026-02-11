from odoo import api, models, fields

from odoo.exceptions import ValidationError


class HrHospitalDisease(models.Model):
    _name = 'hr.hospital.disease'
    _description = 'Disease'
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(required=True)

    active = fields.Boolean(default=True)
    description = fields.Text()

    is_contagious = fields.Boolean(default=False, string='Contagious')

    icd_10 = fields.Char(string='ICD-10', size=10)

    danger_level = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        required=True,
    )

    symptoms = fields.Text()

    region_ids = fields.Many2many(
        comodel_name='res.country',
        help='Countries where the disease is most common',
    )

    parent_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Parent disease',
        index=True,
        ondelete='cascade'
    )

    child_ids = fields.One2many(
        comodel_name='hr.hospital.disease',
        inverse_name='parent_id',
        string='Child disease'
    )

    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError('Recursive hierarchy created.')
