# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env

# Dynamic schemas
from ..partner_schemas import PartnerCreate

router = APIRouter()


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
    data: PartnerCreate,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
):
    """Create a new res.partner."""
    Partner = env["res.partner"]
    if Partner.search_count([("ref", "=", data.ref)]):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Reference already exists"
        )
    vals = data.dict(exclude_unset=True)  # includes any dynamically-registered fields
    new_partner = Partner.create(vals)
    return {"id": new_partner.id, "name": new_partner.name, "ref": new_partner.ref}


# # Update endpoint scaffold – logic to be implemented later
# @router.patch(  # PATCH for partial update; keeps PUT free if you prefer full replace
#     "/partner/{partner_id}",
#     response_model=PartnerResponse,
#     status_code=status.HTTP_202_ACCEPTED,
# )
# def update_partner(  # placeholder – business logic will be added later
#     partner_id: int,
#     data: PartnerUpdate,
#     env: Annotated[Environment, Depends(authenticated_partner_env)],
# ):
#     """
#     Update an existing partner.

#     The implementation is intentionally left out for now; only the
#     schema and route are defined so that clients can already see the
#     endpoint in the OpenAPI docs.
#     """
#     raise HTTPException(
#         status.HTTP_501_NOT_IMPLEMENTED,
#         detail="Partner update endpoint not implemented yet",
#     )
