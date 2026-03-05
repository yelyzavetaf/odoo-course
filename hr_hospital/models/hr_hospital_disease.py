from odoo import _, api, models, fields

from odoo.exceptions import ValidationError


class HrHospitalDisease(models.Model):
    """
    Model for managing a hierarchical classifier of diseases.

    This model supports parent-child relationships using the Odoo Nested Sets
    (parent_store) feature for efficient tree traversal. It includes ICD-10
    coding, danger levels, and multi-language support for names and descriptions.
    """
    _name = 'hr.hospital.disease'
    _description = 'Disease'
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(required=True, translate="True")

    active = fields.Boolean(default=True)
    description = fields.Text(translate="True")

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

    symptoms = fields.Text(translate="True")

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
        """
        Validate that the disease hierarchy does not contain recursive loops.

        Uses the built-in Odoo _has_cycle() method to ensure a record
        cannot be its own ancestor.

        :raises ValidationError: If a recursive loop is detected.
        """
        if self._has_cycle():
            raise ValidationError(_('Recursive hierarchy created.'))
