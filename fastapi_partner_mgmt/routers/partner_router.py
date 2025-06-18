# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env

router = APIRouter()


class PartnerCreate(BaseModel):
    name: str
    ref: str
    line_display_name: str
    line_profile_image_url: str


class PartnerResponse(BaseModel):
    id: int
    name: str
    ref: str


@router.post(
    "/partner/create",
    response_model=PartnerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_partner(
    data: PartnerCreate, env: Annotated[Environment, Depends(authenticated_partner_env)]
):
    Partner = env["res.partner"]
    if Partner.search_count([("ref", "=", data.ref)]):
        raise HTTPException(400, "Reference already exists")
    new_partner = Partner.create(
        {
            "name": data.name,
            "ref": data.ref,
            "line_display_name": data.line_display_name,
            "line_profile_image_url": data.line_profile_image_url,
        }
    )
    return {"id": new_partner.id, "name": new_partner.name, "ref": new_partner.ref}
