# Health-e Pro Menu

Pull your child's school lunch (or breakfast) menu directly from Health-e Pro into Home Assistant — no OCR, no screenshots, no manual data entry.

## Setup

1. Find your school's public menu page at `menus.healthepro.com`
2. Copy the full URL from your browser
3. In Home Assistant → Settings → Integrations → Add Integration → **Health-e Pro Menu**
4. Paste the URL and click Submit

That's it. Three sensors are created automatically:

| Sensor | What it shows |
| --- | --- |
| `sensor.*_today` | Today's entrées (or "No school" on off-days) |
| `sensor.*_tomorrow` | Tomorrow's entrées |
| `sensor.*_month` | Full month data in attributes |

## Lovelace card

```yaml
type: markdown
content: |
  {% set s = 'sensor.YOUR_SENSOR_TODAY' %}
  ## Today's Lunch
  {% if state_attr(s, 'off_day') %}
  **No school** — {{ state_attr(s, 'off_day_reason') }}
  {% elif states(s) in ['unknown','unavailable'] %}
  _Menu unavailable_
  {% else %}
  **Entrées:** {{ state_attr(s, 'entrees') | join(', ') }}
  {% set t = state_attr(s, 'sections') or {} %}
  {% for label in ['Vegetables','Fruit','Milk'] %}{% if t.get(label) %}
  **{{ label }}:** {{ t[label] | join(', ') }}{% endif %}{% endfor %}
  {% endif %}
```

## Works with any Health-e Pro school

The integration auto-discovers your school's details from the URL — no hardcoded IDs.
Add it multiple times for different menus (e.g., breakfast + lunch).
