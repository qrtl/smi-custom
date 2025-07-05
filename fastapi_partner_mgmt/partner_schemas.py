# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Dynamic Pydantic schemas for the FastAPI ↔ Odoo partner API.

* PartnerCreate: required base fields (`name`, `ref`) + any extra fields
* PartnerUpdate: same fields but *all optional* (PATCH semantics)

Shim add-ons call `register_partner_field()` to extend BOTH schemas.
"""

import logging
from typing import Any

import pydantic
from pydantic import BaseModel

_logger = logging.getLogger(__name__)


__all__ = [
    "PartnerCreate",
    "PartnerUpdate",
    "register_partner_field",
    "clear_partner_field_registry",
]


# Helper: version-aware create_model
def _create_model(name: str, fields: dict, *, forbid_extra: bool) -> type[BaseModel]:
    """Wrapper so we don't care which major Pydantic version is installed."""
    if pydantic.version.VERSION.startswith("2"):
        # Pydantic ≥ 2.0
        from pydantic import ConfigDict  # lazy import to avoid v1 failure

        cfg = ConfigDict(extra="forbid" if forbid_extra else "ignore")
        return pydantic.create_model(
            name,
            __base__=BaseModel,
            __config__=cfg,  # v2 uses __config__
            **fields,
        )
    # Pydantic 1.x fallback
    return pydantic.create_model(  # type: ignore[call-arg]
        name,
        **fields,
        __config__=type(
            "Cfg",
            (),
            {"extra": "forbid" if forbid_extra else "ignore"},
        ),
    )


# Internal registry: {"field_name": (annotation, default)}
_REGISTRY: dict[str, tuple[type, Any]] = {}


def register_partner_field(name: str, annotation: type, default: Any = None) -> None:
    """Expose a custom field in both PartnerCreate & PartnerUpdate schemas."""
    _REGISTRY[name] = (annotation, default)
    _rebuild_models()


def clear_partner_field_registry() -> None:
    """Remove all previously registered fields (called from post_load hooks)."""
    _REGISTRY.clear()
    _rebuild_models()


# Model builders
def _build_partner_create() -> type[BaseModel]:
    base = {"name": (str, ...), "ref": (str, ...)}
    fields = {**base, **_REGISTRY}
    return _create_model("PartnerCreate", fields, forbid_extra=True)


def _build_partner_update() -> type[BaseModel]:
    # every field optional → default None (or provided default)
    fields = {
        fname: (ftype, None if default is ... else default)
        for fname, (ftype, default) in _REGISTRY.items()
    }
    fields.update({"name": (str, None), "ref": (str, None)})
    return _create_model("PartnerUpdate", fields, forbid_extra=True)


def _rebuild_models() -> None:
    """Re-generate both public models after any registry change."""
    global PartnerCreate, PartnerUpdate
    PartnerCreate = _build_partner_create()
    PartnerUpdate = _build_partner_update()


try:
    import importlib

    bridge = importlib.import_module("odoo.addons.fastapi_partner_mgmt_field")
    for name, typ, default in getattr(bridge, "EXTRA_PARTNER_FIELDS", []):
        _REGISTRY[name] = (typ, default)
except ModuleNotFoundError:
    _logger.debug(
        "Optional module 'fastapi_partner_mgmt_field' not found; "
        "skipping extra partner‐field registration",
        exc_info=True,
    )

_logger = logging.getLogger(__name__)
_logger.info("Partner schema build-time registry = %s", _REGISTRY)

# Initial build on import
PartnerCreate: type[BaseModel]
PartnerUpdate: type[BaseModel]
_rebuild_models()
