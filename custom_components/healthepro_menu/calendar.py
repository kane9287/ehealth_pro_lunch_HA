"""Calendar entity for Health-e Pro Menu."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import HealtheProCoordinator
from .models import MenuDay


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HealtheProCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SchoolMenuCalendar(coordinator, entry)])


def _day_to_event(day: MenuDay) -> CalendarEvent:
    start = date.fromisoformat(day.date)
    end = start + timedelta(days=1)  # all-day events use exclusive end date

    if day.off_day:
        summary = f"No school — {day.off_day_reason}" if day.off_day_reason else "No school"
        description = None
    else:
        summary = ", ".join(day.entrees) if day.entrees else "Lunch available"
        lines = []
        for section, items in day.sections.items():
            if items:
                lines.append(f"{section}: {', '.join(items)}")
        if day.allergens:
            lines.append(f"\n⚠️ Contains: {', '.join(day.allergens)}")
        description = "\n".join(lines) if lines else None

    return CalendarEvent(start=start, end=end, summary=summary, description=description)


class SchoolMenuCalendar(CoordinatorEntity[HealtheProCoordinator], CalendarEntity):
    _attr_has_entity_name = True
    _attr_name = "Menu"

    def __init__(self, coordinator: HealtheProCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    @property
    def device_info(self) -> DeviceInfo:
        cfg = self._entry.data
        return DeviceInfo(
            identifiers={(DOMAIN, f"{cfg['org_id']}:{cfg['site_id']}:{cfg['menu_id']}")},
            name=self._entry.title,
            manufacturer="Health-e Pro",
            model=cfg.get("meal_type_label", "Lunch"),
            configuration_url=cfg["source_url"],
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def event(self) -> CalendarEvent | None:
        """Return today's event, or the next upcoming one."""
        if not self.coordinator.data:
            return None
        today = dt_util.now().date()
        for month in [self.coordinator.data.current_month, self.coordinator.data.next_month]:
            if not month:
                continue
            for day in month.days:
                d = date.fromisoformat(day.date)
                if d >= today:
                    return _day_to_event(day)
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return all events within the requested range."""
        if not self.coordinator.data:
            return []

        range_start = start_date.date()
        range_end = end_date.date()
        events: list[CalendarEvent] = []

        for month in [self.coordinator.data.current_month, self.coordinator.data.next_month]:
            if not month:
                continue
            for day in month.days:
                d = date.fromisoformat(day.date)
                if range_start <= d < range_end:
                    events.append(_day_to_event(day))

        return events
