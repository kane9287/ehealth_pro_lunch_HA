"""Async HTTP client for Health-e Pro public menu endpoints."""
from __future__ import annotations

import asyncio
import logging
from importlib.metadata import version as pkg_version

import aiohttp

from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

try:
    _VERSION = pkg_version("healthepro_menu")
except Exception:
    _VERSION = "0.0.0"

_HEADERS = {
    "User-Agent": f"HomeAssistant-HealtheProMenu/{_VERSION}",
    "Accept": "application/json",
}
_TIMEOUT = aiohttp.ClientTimeout(total=20)


class HealtheProApiError(Exception):
    """Raised when an API call fails."""


class HealtheProApi:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _get(self, path: str) -> dict | list:
        url = f"{BASE_URL}{path}"
        try:
            async with self._session.get(url, headers=_HEADERS, timeout=_TIMEOUT) as resp:
                if resp.status == 404:
                    raise HealtheProApiError(f"Not found: {url}")
                if resp.status != 200:
                    raise HealtheProApiError(f"HTTP {resp.status} from {url}")
                return await resp.json()
        except asyncio.TimeoutError as err:
            raise HealtheProApiError(f"Timeout fetching {url}") from err
        except aiohttp.ClientError as err:
            raise HealtheProApiError(f"Request error: {err}") from err

    async def async_get_organization(self, org_id: int) -> dict:
        result = await self._get(f"/organizations/{org_id}")
        return result.get("data", result) if isinstance(result, dict) else result

    async def async_get_site(self, org_id: int, site_id: int) -> dict:
        result = await self._get(f"/organizations/{org_id}/sites/{site_id}")
        return result.get("data", result) if isinstance(result, dict) else result

    async def async_get_site_menus(self, org_id: int, site_id: int) -> list[dict]:
        result = await self._get(f"/organizations/{org_id}/sites/{site_id}/menus/")
        if isinstance(result, list):
            return result
        data = result.get("data", result) if isinstance(result, dict) else []
        return data if isinstance(data, list) else [data]

    async def async_get_menu(self, org_id: int, menu_id: int) -> dict:
        result = await self._get(f"/organizations/{org_id}/menus/{menu_id}")
        return result.get("data", result) if isinstance(result, dict) else result

    async def async_get_date_overwrites(
        self, org_id: int, menu_id: int, year: int, month: int
    ) -> list[dict]:
        result = await self._get(
            f"/organizations/{org_id}/menus/{menu_id}/year/{year}/month/{month}/date_overwrites"
        )
        return result.get("data", []) if isinstance(result, dict) else []

    async def async_get_recipes(
        self, org_id: int, menu_id: int, start_date: str, end_date: str
    ) -> list[dict]:
        result = await self._get(
            f"/organizations/{org_id}/menus/{menu_id}/start_date/{start_date}/end_date/{end_date}/recipes/"
        )
        if isinstance(result, list):
            return result
        return result.get("data", []) if isinstance(result, dict) else []

    async def async_get_allergens(self, org_id: int) -> list[dict]:
        result = await self._get(f"/organizations/{org_id}/allergens")
        if isinstance(result, list):
            return result
        return result.get("data", []) if isinstance(result, dict) else []

    async def async_get_attributes(self, org_id: int) -> list[dict]:
        result = await self._get(f"/organizations/{org_id}/attributes")
        if isinstance(result, list):
            return result
        return result.get("data", []) if isinstance(result, dict) else []
