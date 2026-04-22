"""Diagnostics support for Health-e Pro Menu."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    data = coordinator.data
    month_summary = None
    if data and data.current_month:
        month_summary = {
            "year": data.current_month.year,
            "month": data.current_month.month,
            "day_count": len(data.current_month.days),
            "off_days": [
                d.date for d in data.current_month.days if d.off_day
            ],
        }

    return {
        "config_entry": {
            "domain": entry.domain,
            "version": entry.version,
            "title": entry.title,
            "data": {k: v for k, v in entry.data.items() if k != "source_url"},
            "source_url": entry.data.get("source_url"),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update": str(coordinator.last_update_success),
            "last_error": data.last_error if data else None,
        },
        "data_summary": {
            "organization": data.organization_name if data else None,
            "site": data.site_name if data else None,
            "menu": data.menu_name if data else None,
            "meal_type": data.meal_type_label if data else None,
            "published_months": data.published_months if data else [],
            "current_month": month_summary,
            "next_month_loaded": data.next_month is not None if data else False,
        },
    }
