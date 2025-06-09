# Copyright 2025 Quartile (https://www/quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env

router = APIRouter()


class PartnerCreate(BaseModel):
    name: str


@router.post("/partner/create")
def create_partner(
    data: PartnerCreate, env: Annotated[Environment, Depends(authenticated_partner_env)]
):
    Partner = env["res.partner"]
    if Partner.search_count([("name", "=", data.name)]):
        raise HTTPException(400, "Partner already exists")
    partner = Partner.create({"name": data.name})
    return {"id": partner.id, "name": partner.name}
