import os
import sys


PACKAGE_NAME = "fastword"
LEGACY_PACKAGE_NAME = "autoword"


def app_root() -> str:
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(__file__)


def resource_path(*parts: str) -> str:
    primary = os.path.join(app_root(), *parts)
    if os.path.exists(primary):
        return primary

    fallback = os.path.join(app_root(), PACKAGE_NAME, *parts)
    if os.path.exists(fallback):
        return fallback

    legacy_fallback = os.path.join(app_root(), LEGACY_PACKAGE_NAME, *parts)
    if os.path.exists(legacy_fallback):
        return legacy_fallback

    return primary


def project_root() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
