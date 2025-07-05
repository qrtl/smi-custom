# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models

from ..routers.partner_router import router as partnerapi_router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app = fields.Selection(
        selection_add=[("partnerapi", "Partner API")],
        ondelete={"partnerapi": "cascade"},
    )

    def _get_fastapi_routers(self):
        if self.app == "partnerapi":
            return [partnerapi_router]
        return super()._get_fastapi_routers()
