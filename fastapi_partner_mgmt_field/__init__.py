# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Simply defines EXTRA_PARTNER_FIELDS so that fastapi_partner_mgmt can
discover them *before* building its schema.
"""

EXTRA_PARTNER_FIELDS: list[tuple[str, type, object]] = [
    ("line_display_name", str, None),
    ("line_profile_image_url", str, None),
    # add more tuples as needed.
]
