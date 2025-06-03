# Copyright 2025 Quartile (https://www/quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..routers.routes import router as userapi_router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app = fields.Selection(
        selection_add=[("userapi", "User API")],
        ondelete={"userapi": "cascade"},
    )

    def _get_fastapi_routers(self):
        if self.app == "userapi":
            return [userapi_router]
        return super()._get_fastapi_routers()
