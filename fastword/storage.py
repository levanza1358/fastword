import json
import os
import shutil
from datetime import datetime


APP_NAME = "FastWord"
LEGACY_APP_NAME = "AutoWord"


def default_rules():
    return [
        {"trigger": "/up", "replacement": "WASDWASD", "enabled": True},
    ]


def default_settings() -> dict:
    return {
        "auto_enter": True,
        "global_delay_ms": 120,
        "tray_enabled": True,
        "minimize_to_tray": False,
        "start_with_windows": False,
        "engine_auto_start": False,
    }


def _data_dir() -> str:
    base = os.getenv("APPDATA") or os.getcwd()
    folder = os.path.join(base, APP_NAME)
    legacy_folder = os.path.join(base, LEGACY_APP_NAME)
    if not os.path.exists(folder) and os.path.isdir(legacy_folder):
        try:
            shutil.copytree(legacy_folder, folder, dirs_exist_ok=True)
        except Exception:
            pass
    os.makedirs(folder, exist_ok=True)
    return folder


def _rules_path() -> str:
    return os.path.join(_data_dir(), "rules.json")


def _read_data() -> dict | None:
    path = _rules_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return None


def load_config() -> dict:
    data = _read_data() or {}
    settings = data.get("settings", {})
    if isinstance(settings, dict):
        return normalize_settings(settings)
    settings = default_settings()
    existing_rules = data.get("rules", []) if isinstance(data.get("rules", []), list) else default_rules()
    _write_data(existing_rules, settings)
    return settings


def load_rules() -> list[dict]:
    data = _read_data() or {}
    rules = data.get("rules", [])
    if isinstance(rules, list):
        return [r for r in rules if isinstance(r, dict)]
    rules = default_rules()
    settings = data.get("settings", {}) if isinstance(data.get("settings", {}), dict) else default_settings()
    _write_data(rules, settings)
    return rules


def save_rules(rules: list[dict]) -> None:
    data = _read_data() or {}
    config = data.get("settings", {}) if isinstance(data.get("settings", {}), dict) else default_settings()
    _write_data(list(rules or []), config)


def save_config(settings: dict) -> None:
    data = _read_data() or {}
    rules = data.get("rules", []) if isinstance(data.get("rules", []), list) else default_rules()
    _write_data(rules, normalize_settings(settings))


def load_data() -> dict:
    data = _read_data() or {}
    rules = data.get("rules", [])
    settings = data.get("settings", {})
    if not isinstance(rules, list):
        rules = default_rules()
    if not isinstance(settings, dict):
        settings = default_settings()
    return {
        "rules": [r for r in rules if isinstance(r, dict)],
        "settings": normalize_settings(settings),
    }


def save_data(rules: list[dict], settings: dict) -> None:
    _write_data(list(rules or []), normalize_settings(settings))


def export_data(path: str, rules: list[dict], settings: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "rules": list(rules or []),
                "settings": normalize_settings(settings),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def import_data(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rules = data.get("rules", [])
    settings = data.get("settings", {})
    if not isinstance(rules, list):
        raise ValueError("Backup file has an invalid rules format.")
    if not isinstance(settings, dict):
        raise ValueError("Backup file has an invalid settings format.")

    return {
        "rules": [r for r in rules if isinstance(r, dict)],
        "settings": normalize_settings(settings),
    }


def create_backup(rules: list[dict], settings: dict) -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(_data_dir(), f"backup-{timestamp}.json")
    export_data(path, rules, settings)
    return path


def data_dir() -> str:
    return _data_dir()


def _write_data(rules: list[dict], settings: dict) -> None:
    path = _rules_path()
    data = {
        "rules": list(rules or []),
        "settings": normalize_settings(settings),
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def rules_path() -> str:
    return _rules_path()


def normalize_settings(settings: dict | None) -> dict:
    merged = default_settings()
    merged.update(settings or {})
    merged.pop("close_to_tray", None)
    merged["auto_enter"] = bool(merged.get("auto_enter", True))
    merged["tray_enabled"] = bool(merged.get("tray_enabled", True))
    merged["minimize_to_tray"] = bool(merged.get("minimize_to_tray", False))
    merged["start_with_windows"] = bool(merged.get("start_with_windows", False))
    merged["engine_auto_start"] = bool(merged.get("engine_auto_start", False))
    try:
        merged["global_delay_ms"] = max(0, int(merged.get("global_delay_ms", 120)))
    except Exception:
        merged["global_delay_ms"] = 120
    return merged

