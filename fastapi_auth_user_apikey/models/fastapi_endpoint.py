# Copyright 2025 Quartile (https://www/quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from odoo import fields, models
from odoo.api import Environment

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import fastapi_endpoint, odoo_env


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    auth_method = fields.Selection(
        selection=[("api_key", "Api Key"), ("http_basic", "HTTP Basic")],
        string="Authenciation method",
    )
    user_ids = fields.Many2many("res.users", relation="endpoint_user_rel")


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
    endpoint: Annotated[models.Model, Depends(fastapi_endpoint)],
) -> Partner:
    uid = env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
    if not uid or endpoint.id not in env["res.users"].browse(uid).endpoint_ids.ids:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
    return env["res.users"].sudo().browse(uid).partner_id
