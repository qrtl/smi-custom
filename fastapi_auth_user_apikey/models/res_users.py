# Copyright 2025 Quartile (https://www/quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    endpoint_ids = fields.Many2many("fastapi.endpoint", relation="endpoint_user_rel")
