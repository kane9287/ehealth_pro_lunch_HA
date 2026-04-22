"""Config flow for Health-e Pro Menu integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HealtheProApi, HealtheProApiError
from .const import (
    CONF_CUSTOM_NAME,
    CONF_INCLUDE_PRICES,
    CONF_INCLUDE_RECIPE_DETAILS,
    CONF_INCLUDE_SIDEBARS,
    CONF_MEAL_TYPE_ID,
    CONF_MENU_ID,
    CONF_ORG_ID,
    CONF_PREFETCH_NEXT_MONTH,
    CONF_REFRESH_HOURS,
    CONF_SITE_ID,
    CONF_SOURCE_URL,
    DEFAULT_INCLUDE_PRICES,
    DEFAULT_INCLUDE_RECIPE_DETAILS,
    DEFAULT_INCLUDE_SIDEBARS,
    DEFAULT_PREFETCH_NEXT_MONTH,
    DEFAULT_REFRESH_HOURS,
    DOMAIN,
    MEAL_TYPE_LABELS,
)
from .parser import parse_menu_url

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCE_URL): str,
        vol.Optional(CONF_CUSTOM_NAME): str,
    }
)


class HealtheProMenuConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Health-e Pro Menu."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_SOURCE_URL].strip()
            ids = parse_menu_url(url)

            if ids is None:
                errors[CONF_SOURCE_URL] = "invalid_url"
            else:
                org_id, site_id, menu_id = ids
                session = async_get_clientsession(self.hass)
                api = HealtheProApi(session)

                try:
                    org, site, site_menus, menu_meta = await _fetch_discovery(
                        api, org_id, site_id, menu_id
                    )
                except HealtheProApiError as err:
                    _LOGGER.debug("Discovery error: %s", err)
                    errors[CONF_SOURCE_URL] = "cannot_connect"
                else:
                    # Validate menu belongs to site
                    menu_ids_on_site = {m.get("id") or m.get("menu_id") for m in site_menus}
                    # Flexible ID matching — try both 'id' and 'menu_id' keys
                    found = any(
                        str(m.get("id", "")) == str(menu_id) or
                        str(m.get("menu_id", "")) == str(menu_id)
                        for m in site_menus
                    )
                    if not found:
                        _LOGGER.debug(
                            "menu_id %s not found in site menus: %s", menu_id, site_menus
                        )
                        # Non-blocking — site_menus response shape may vary; proceed with warning
                        _LOGGER.warning(
                            "Could not confirm menu %s belongs to site %s; proceeding anyway",
                            menu_id, site_id,
                        )

                    published_months = menu_meta.get("published_months", [])
                    if not published_months:
                        errors[CONF_SOURCE_URL] = "no_published_months"
                    else:
                        # Determine meal_type_id from site_menus list
                        meal_type_id = 2  # default lunch
                        for m in site_menus:
                            m_id = m.get("id") or m.get("menu_id")
                            if str(m_id) == str(menu_id):
                                meal_type_id = m.get("meal_type_id", 2)
                                break

                        unique_id = f"{org_id}:{site_id}:{menu_id}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured()

                        org_name = org.get("name", str(org_id))
                        site_name = site.get("name", str(site_id))
                        menu_name = menu_meta.get("name", str(menu_id))
                        meal_label = MEAL_TYPE_LABELS.get(meal_type_id, "Lunch")

                        custom_name = user_input.get(CONF_CUSTOM_NAME, "").strip()
                        title = custom_name or f"{site_name} — {menu_name}"

                        return self.async_create_entry(
                            title=title,
                            data={
                                CONF_SOURCE_URL: url,
                                CONF_CUSTOM_NAME: custom_name,
                                CONF_ORG_ID: org_id,
                                CONF_SITE_ID: site_id,
                                CONF_MENU_ID: menu_id,
                                CONF_MEAL_TYPE_ID: meal_type_id,
                                "organization_name": org_name,
                                "site_name": site_name,
                                "menu_name": menu_name,
                                "meal_type_label": meal_label,
                            },
                        )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
            description_placeholders={
                "example_url": (
                    "https://menus.healthepro.com/organizations/2169/sites/13982/menus/92206"
                )
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return HealtheProOptionsFlow()


async def _fetch_discovery(
    api: HealtheProApi, org_id: int, site_id: int, menu_id: int
) -> tuple[dict, dict, list, dict]:
    """Fetch org, site, site menus, and menu metadata concurrently."""
    import asyncio

    org_task = asyncio.create_task(api.async_get_organization(org_id))
    site_task = asyncio.create_task(api.async_get_site(org_id, site_id))
    site_menus_task = asyncio.create_task(api.async_get_site_menus(org_id, site_id))
    menu_task = asyncio.create_task(api.async_get_menu(org_id, menu_id))

    results = await asyncio.gather(
        org_task, site_task, site_menus_task, menu_task, return_exceptions=True
    )

    for result in results:
        if isinstance(result, Exception):
            raise HealtheProApiError(str(result)) from result

    return results[0], results[1], results[2], results[3]


class HealtheProOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        opts = self.config_entry.options

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_REFRESH_HOURS,
                        default=opts.get(CONF_REFRESH_HOURS, DEFAULT_REFRESH_HOURS),
                    ): vol.All(int, vol.Range(min=1, max=24)),
                    vol.Optional(
                        CONF_PREFETCH_NEXT_MONTH,
                        default=opts.get(CONF_PREFETCH_NEXT_MONTH, DEFAULT_PREFETCH_NEXT_MONTH),
                    ): bool,
                    vol.Optional(
                        CONF_INCLUDE_RECIPE_DETAILS,
                        default=opts.get(CONF_INCLUDE_RECIPE_DETAILS, DEFAULT_INCLUDE_RECIPE_DETAILS),
                    ): bool,
                    vol.Optional(
                        CONF_INCLUDE_PRICES,
                        default=opts.get(CONF_INCLUDE_PRICES, DEFAULT_INCLUDE_PRICES),
                    ): bool,
                    vol.Optional(
                        CONF_INCLUDE_SIDEBARS,
                        default=opts.get(CONF_INCLUDE_SIDEBARS, DEFAULT_INCLUDE_SIDEBARS),
                    ): bool,
                }
            ),
        )
