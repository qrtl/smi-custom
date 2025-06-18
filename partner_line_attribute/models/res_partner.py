# Copyright 2025 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    line_display_name = fields.Char("LINE Display Name", copy=False)
    line_profile_image_url = fields.Char("LINE Profile Image URL", copy=False)
