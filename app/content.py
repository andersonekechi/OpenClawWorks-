from __future__ import annotations

from datetime import datetime
from typing import Any


def build_post_text(template: str) -> str:
    """
    Build post text from a template.
    Supports:
      - {date}: YYYY-MM-DD
      - {datetime}: YYYY-MM-DD HH:MM
    """
    now = datetime.now()
    values: dict[str, Any] = {
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime("%Y-%m-%d %H:%M"),
    }
    return template.format(**values)


def load_templates_from_text(raw: str) -> list[str]:
    templates = [line.strip() for line in raw.splitlines() if line.strip()]
    if not templates:
        raise ValueError("No post templates found in posts file.")
    return templates
