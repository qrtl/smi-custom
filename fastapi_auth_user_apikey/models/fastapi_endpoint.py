# Copyright 2025 Quartile (https://www/quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from odoo import fields, models
from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner_impl,
    fastapi_endpoint,
    odoo_env,
)


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    use_user_apikey_auth = fields.Boolean(
        string="Use User API-key Authentication",
        help="If checked, this endpoint will use the API-key authentication method "
        "based on user records.",
    )
    apikey_auth_user_ids = fields.Many2many(
        "res.users",
        string="API-key Auth Users",
        relation="endpoint_user_rel",
        help="Users allowed to access this endpoint with API Key.",
    )

    def _get_app_dependencies_overrides(self):
        res = super()._get_app_dependencies_overrides()
        if self.use_user_apikey_auth:
            res[authenticated_partner_impl] = (
                authenticated_partner_from_apikey_auth_user
            )
        return res


def authenticated_partner_from_apikey_auth_user(
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
    endpoint: Annotated[models.Model, Depends(fastapi_endpoint)],
) -> Partner:
    uid = env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key is invalid."
        )
    if endpoint.id not in env["res.users"].browse(uid).endpoint_ids.ids:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not allowed to access the endpoint.",
        )
    return env["res.users"].sudo().browse(uid).partner_id
