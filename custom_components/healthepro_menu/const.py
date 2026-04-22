"""Constants for the Health-e Pro Menu integration."""

DOMAIN = "healthepro_menu"
BASE_URL = "https://menus.healthepro.com/api"
MENU_HOST = "menus.healthepro.com"

DEFAULT_REFRESH_HOURS = 24
DEFAULT_PREFETCH_NEXT_MONTH = True
DEFAULT_INCLUDE_RECIPE_DETAILS = False
DEFAULT_INCLUDE_PRICES = False
DEFAULT_INCLUDE_SIDEBARS = False

CONF_SOURCE_URL = "source_url"
CONF_CUSTOM_NAME = "custom_name"
CONF_ORG_ID = "org_id"
CONF_SITE_ID = "site_id"
CONF_MENU_ID = "menu_id"
CONF_MEAL_TYPE_ID = "meal_type_id"
CONF_REFRESH_HOURS = "refresh_hours"
CONF_PREFETCH_NEXT_MONTH = "prefetch_next_month"
CONF_INCLUDE_RECIPE_DETAILS = "include_recipe_details"
CONF_INCLUDE_PRICES = "include_prices"
CONF_INCLUDE_SIDEBARS = "include_sidebars"

ATTR_DATE = "date"
ATTR_OFF_DAY = "off_day"
ATTR_OFF_DAY_REASON = "off_day_reason"
ATTR_ENTREES = "entrees"
ATTR_SECTIONS = "sections"
ATTR_NOTES = "notes"
ATTR_MEAL_TYPE = "meal_type"
ATTR_SOURCE_URL = "source_url"
ATTR_ORGANIZATION_NAME = "organization_name"
ATTR_SITE_NAME = "site_name"
ATTR_MENU_NAME = "menu_name"
ATTR_DAYS = "days"
ATTR_PUBLISHED_MONTHS = "published_months"
ATTR_LAST_ERROR = "last_error"

MEAL_TYPE_BREAKFAST = 1
MEAL_TYPE_LUNCH = 2
MEAL_TYPE_LABELS = {
    MEAL_TYPE_BREAKFAST: "Breakfast",
    MEAL_TYPE_LUNCH: "Lunch",
}
MEAL_ENTREE_CATEGORIES = {
    MEAL_TYPE_BREAKFAST: "Breakfast Entree",
    MEAL_TYPE_LUNCH: "Lunch Entree",
}
