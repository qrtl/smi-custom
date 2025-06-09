# Copyright 2025 Quartile (https://www/quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from odoo import fields, models
from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner_from_basic_auth_user,
    authenticated_partner_impl,
    odoo_env,
)

from ..routers.partner_router import router as partnerapi_router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app = fields.Selection(
        selection_add=[("partnerapi", "Partner API")],
        ondelete={"partnerapi": "cascade"},
    )
    auth_method = fields.Selection(
        selection=[("api_key", "Api Key"), ("http_basic", "HTTP Basic")],
        string="Authenciation method",
    )

    def _get_fastapi_routers(self):
        if self.app == "partnerapi":
            return [partnerapi_router]
        return super()._get_fastapi_routers()

    def _get_app_dependencies_overrides(self):
        res = super()._get_app_dependencies_overrides()
        if self.app == "partnerapi":
            if self.auth_method == "http_basic":
                res[authenticated_partner_impl] = (
                    authenticated_partner_from_basic_auth_user
                )
            else:  # "api_key"
                res[authenticated_partner_impl] = (
                    api_key_based_authenticated_partner_impl_custom
                )
        return res


def api_key_based_authenticated_partner_impl_custom(
    api_key: Annotated[
        str,
        Depends(
            APIKeyHeader(
                name="api-key",
                description="We match the API key against user's API key records.",
            )
        ),
    ],
    env: Annotated[Environment, Depends(odoo_env)],
) -> Partner:
    uid = env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
    return env["res.users"].sudo().browse(uid).partner_id
