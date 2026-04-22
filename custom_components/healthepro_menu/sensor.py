"""Sensor entities for Health-e Pro Menu."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_DATE,
    ATTR_DAYS,
    ATTR_ENTREES,
    ATTR_LAST_ERROR,
    ATTR_MEAL_TYPE,
    ATTR_MENU_NAME,
    ATTR_NOTES,
    ATTR_OFF_DAY,
    ATTR_OFF_DAY_REASON,
    ATTR_ORGANIZATION_NAME,
    ATTR_PUBLISHED_MONTHS,
    ATTR_SECTIONS,
    ATTR_SITE_NAME,
    ATTR_SOURCE_URL,
    DOMAIN,
)
from .coordinator import HealtheProCoordinator
from .models import MenuDay, SchoolMenuData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HealtheProCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SchoolMenuTodaySensor(coordinator, entry),
            SchoolMenuTomorrowSensor(coordinator, entry),
            SchoolMenuMonthSensor(coordinator, entry),
        ]
    )


def _day_state(day: MenuDay | None) -> str:
    if day is None:
        return "Menu unavailable"
    if day.off_day:
        return "No school"
    if not day.entrees:
        return "Menu available"
    return ", ".join(day.entrees)


def _day_attrs(day: MenuDay | None, data: SchoolMenuData) -> dict:
    base = {
        ATTR_ORGANIZATION_NAME: data.organization_name,
        ATTR_SITE_NAME: data.site_name,
        ATTR_MENU_NAME: data.menu_name,
        ATTR_MEAL_TYPE: data.meal_type_label,
        ATTR_SOURCE_URL: data.source_url,
    }
    if day is None:
        return {**base, ATTR_DATE: None, ATTR_OFF_DAY: None, ATTR_ENTREES: [], ATTR_SECTIONS: {}}
    attrs = {
        **base,
        ATTR_DATE: day.date,
        ATTR_OFF_DAY: day.off_day,
        ATTR_OFF_DAY_REASON: day.off_day_reason,
        ATTR_ENTREES: day.entrees,
        ATTR_SECTIONS: day.sections,
        ATTR_NOTES: day.notes,
    }
    if day.recipes:
        attrs["allergens"] = day.allergens
        attrs["recipes"] = {str(k): v.to_dict() for k, v in day.recipes.items()}
    return attrs


class _BaseMenuSensor(CoordinatorEntity[HealtheProCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: HealtheProCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        cfg = entry.data
        self._device_id = f"{cfg['org_id']}:{cfg['site_id']}:{cfg['menu_id']}"

    @property
    def device_info(self) -> DeviceInfo:
        cfg = self._entry.data
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._entry.title,
            manufacturer="Health-e Pro",
            model=cfg.get("meal_type_label", "Lunch"),
            configuration_url=cfg["source_url"],
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


class SchoolMenuTodaySensor(_BaseMenuSensor):
    _attr_icon = "mdi:food-apple"

    def __init__(self, coordinator: HealtheProCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_today"
        self._attr_name = "Today"

    @property
    def native_value(self) -> str:
        if not self.coordinator.data:
            return "Menu unavailable"
        today = dt_util.now().strftime("%Y-%m-%d")
        day = self.coordinator.data.get_day(today)
        return _day_state(day)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        today = dt_util.now().strftime("%Y-%m-%d")
        day = self.coordinator.data.get_day(today)
        return _day_attrs(day, self.coordinator.data)


class SchoolMenuTomorrowSensor(_BaseMenuSensor):
    _attr_icon = "mdi:food-fork-drink"

    def __init__(self, coordinator: HealtheProCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_tomorrow"
        self._attr_name = "Tomorrow"

    @property
    def native_value(self) -> str:
        if not self.coordinator.data:
            return "Menu unavailable"
        tomorrow = (dt_util.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day = self.coordinator.data.get_day(tomorrow)
        return _day_state(day)

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        tomorrow = (dt_util.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day = self.coordinator.data.get_day(tomorrow)
        return _day_attrs(day, self.coordinator.data)


class SchoolMenuMonthSensor(_BaseMenuSensor):
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator: HealtheProCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_month"
        self._attr_name = "Month"

    @property
    def native_value(self) -> str:
        if not self.coordinator.data:
            return "No data"
        data = self.coordinator.data
        count = len(data.current_month.days) if data.current_month else 0
        return f"{count} days loaded"

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        data = self.coordinator.data
        days = []
        if data.current_month:
            days.extend(d.to_dict() for d in data.current_month.days)
        if data.next_month:
            days.extend(d.to_dict() for d in data.next_month.days)
        return {
            ATTR_DAYS: days,
            ATTR_PUBLISHED_MONTHS: data.published_months,
            ATTR_LAST_ERROR: data.last_error,
            ATTR_ORGANIZATION_NAME: data.organization_name,
            ATTR_SITE_NAME: data.site_name,
            ATTR_MENU_NAME: data.menu_name,
            ATTR_SOURCE_URL: data.source_url,
        }
