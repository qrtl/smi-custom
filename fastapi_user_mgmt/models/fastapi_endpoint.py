# Copyright 2025 Quartile (https://www/quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.fastapi.dependencies import (
    authenticated_partner_from_basic_auth_user,
    authenticated_partner_impl,
)
from odoo.addons.fastapi_auth_user_apikey.models.fastapi_endpoint import (
    api_key_based_authenticated_partner_impl_custom,
)

from ..routers.user_router import router as userapi_router


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

    def _get_app_dependencies_overrides(self):
        res = super()._get_app_dependencies_overrides()
        if self.app == "userapi":
            if self.auth_method == "http_basic":
                res[authenticated_partner_impl] = (
                    authenticated_partner_from_basic_auth_user
                )
            else:  # "api_key"
                res[authenticated_partner_impl] = (
                    api_key_based_authenticated_partner_impl_custom
                )
        return res
