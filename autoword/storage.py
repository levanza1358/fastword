import json
import os


def default_rules():
    return [
        {"trigger": "/up", "replacement": "WASDWASD", "enabled": True},
    ]


def _rules_path() -> str:
    base = os.getenv("APPDATA") or os.getcwd()
    folder = os.path.join(base, "AutoWord")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "rules.json")


def load_rules() -> list[dict]:
    path = _rules_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = data.get("rules", [])
        if isinstance(rules, list):
            return [r for r in rules if isinstance(r, dict)]
    except FileNotFoundError:
        pass
    except Exception:
        pass
    rules = default_rules()
    save_rules(rules)
    return rules


def save_rules(rules: list[dict]) -> None:
    path = _rules_path()
    data = {"rules": list(rules or [])}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def rules_path() -> str:
    return _rules_path()

