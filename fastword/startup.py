import os
import sys
import winreg

from .runtime import project_root

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "FastWord"
LEGACY_VALUE_NAME = "AutoWord"


def _launch_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    python_cmd = pythonw if os.path.exists(pythonw) else sys.executable
    main_path = os.path.join(project_root(), "main.py")
    return f'"{python_cmd}" "{main_path}"'


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            for value_name in (VALUE_NAME, LEGACY_VALUE_NAME):
                try:
                    value, _ = winreg.QueryValueEx(key, value_name)
                except FileNotFoundError:
                    continue
                if str(value).strip() == _launch_command():
                    return True
        return False
    except FileNotFoundError:
        return False
    except OSError:
        return False


def set_enabled(enabled: bool) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, _launch_command())
            try:
                winreg.DeleteValue(key, LEGACY_VALUE_NAME)
            except FileNotFoundError:
                pass
        else:
            for value_name in (VALUE_NAME, LEGACY_VALUE_NAME):
                try:
                    winreg.DeleteValue(key, value_name)
                except FileNotFoundError:
                    pass
