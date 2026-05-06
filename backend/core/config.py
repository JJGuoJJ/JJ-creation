"""Configuration loader (YAML based)."""
import os
from pathlib import Path
from typing import Any, Dict
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config_files"
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
REPORTS_DIR = DATA_DIR / "reports"
for d in [DATA_DIR, CACHE_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def load_yaml(filename: str) -> Dict[str, Any]:
    p = CONFIG_DIR / filename
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(filename: str, data: Dict[str, Any]) -> None:
    p = CONFIG_DIR / filename
    # Backup
    if p.exists():
        bak = p.with_suffix(p.suffix + ".bak")
        bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    with open(p, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def get_portfolio() -> Dict[str, Any]:
    return load_yaml("portfolio.yaml").get("current_positions", {})


def get_watchlist() -> Dict[str, Any]:
    return load_yaml("watchlist.yaml").get("watchlist", {})


def get_sectors() -> Dict[str, Any]:
    return load_yaml("sectors.yaml").get("sectors", {})


def get_thresholds() -> Dict[str, Any]:
    return load_yaml("thresholds.yaml")


def get_data_sources() -> Dict[str, Any]:
    return load_yaml("data_sources.yaml")


def get_strategy_profile() -> Dict[str, Any]:
    return load_yaml("strategy_profile.yaml")


SQLITE_PATH = os.environ.get("SQLITE_PATH", str(DATA_DIR / "pib.sqlite"))
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
