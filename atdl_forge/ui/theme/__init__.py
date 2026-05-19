"""UI theme loading."""

import sys
from pathlib import Path


def _theme_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "atdl_forge" / "ui" / "theme" / "light_oms.qss"
    return Path(__file__).parent / "light_oms.qss"


def load_theme() -> str:
    """Load the light OMS stylesheet."""
    path = _theme_path()
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
