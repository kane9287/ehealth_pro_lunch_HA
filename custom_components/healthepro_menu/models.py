"""Data models for Health-e Pro Menu integration."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RecipeDetail:
    id: int
    name: str
    allergens: list[str]
    attributes: list[str]
    calories: float | None
    category: str | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "allergens": self.allergens,
            "attributes": self.attributes,
            "calories": self.calories,
            "category": self.category,
        }


@dataclass
class MenuDay:
    date: str
    off_day: bool
    off_day_reason: str | None
    entrees: list[str]
    sections: dict[str, list[str]]
    recipe_ids: list[int]
    notes: list[str]
    recipes: dict[int, RecipeDetail] = field(default_factory=dict)

    @property
    def allergens(self) -> list[str]:
        """Deduplicated allergen list across all recipes for the day."""
        seen: set[str] = set()
        result: list[str] = []
        for r in self.recipes.values():
            for a in r.allergens:
                if a not in seen:
                    seen.add(a)
                    result.append(a)
        return result

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "off_day": self.off_day,
            "off_day_reason": self.off_day_reason,
            "entrees": self.entrees,
            "sections": self.sections,
            "recipe_ids": self.recipe_ids,
            "notes": self.notes,
            "allergens": self.allergens,
            "recipes": {str(k): v.to_dict() for k, v in self.recipes.items()},
        }


@dataclass
class MenuMonth:
    year: int
    month: int
    days: list[MenuDay] = field(default_factory=list)

    def get_day(self, date_str: str) -> MenuDay | None:
        for day in self.days:
            if day.date == date_str:
                return day
        return None


@dataclass
class SchoolMenuData:
    vendor: str
    organization_id: int
    site_id: int
    menu_id: int
    organization_name: str
    site_name: str
    menu_name: str
    meal_type_id: int
    meal_type_label: str
    published_months: list[str]
    source_url: str
    current_month: MenuMonth | None = None
    next_month: MenuMonth | None = None
    last_error: str | None = None

    def get_day(self, date_str: str) -> MenuDay | None:
        for month in [self.current_month, self.next_month]:
            if month:
                day = month.get_day(date_str)
                if day:
                    return day
        return None
