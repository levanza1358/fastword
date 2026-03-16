from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QSystemTrayIcon

from ..startup import set_enabled as set_startup_enabled
from ..storage import save_config


class WindowSettingsMixin:
    def _load_settings_into_form(self) -> None:
        self.settings_auto_enter_check.setChecked(bool(self.settings.get("auto_enter", True)))
        self.settings_tray_enabled_check.setChecked(bool(self.settings.get("tray_enabled", True)))
        self.settings_minimize_to_tray_check.setChecked(bool(self.settings.get("minimize_to_tray", False)))
        self.settings_startup_check.setChecked(bool(self.settings.get("start_with_windows", False)))
        self.settings_engine_auto_start_check.setChecked(bool(self.settings.get("engine_auto_start", False)))
        self.settings_delay_spin.setValue(int(self.settings.get("global_delay_ms", 120)))
        self._sync_minimize_checkbox_state()

    def _sync_minimize_checkbox_state(self) -> None:
        tray_allowed = self.settings_tray_enabled_check.isChecked() and QSystemTrayIcon.isSystemTrayAvailable()
        self.settings_minimize_to_tray_check.setEnabled(tray_allowed)
        if not tray_allowed:
            self.settings_minimize_to_tray_check.setChecked(False)

    def _save_settings_page(self) -> None:
        tray_enabled = self.settings_tray_enabled_check.isChecked()
        minimize_to_tray = self.settings_minimize_to_tray_check.isChecked() and tray_enabled

        settings = {
            "auto_enter": self.settings_auto_enter_check.isChecked(),
            "global_delay_ms": int(self.settings_delay_spin.value()),
            "tray_enabled": tray_enabled,
            "minimize_to_tray": minimize_to_tray,
            "start_with_windows": self.settings_startup_check.isChecked(),
            "engine_auto_start": self.settings_engine_auto_start_check.isChecked(),
        }

        try:
            set_startup_enabled(settings["start_with_windows"])
        except Exception as exc:
            QMessageBox.critical(self, "Startup Error", f"Failed to update Windows startup: {exc}")
            return

        self.settings = settings
        save_config(self.settings)
        self.engine.configure(
            auto_enter=self.settings.get("auto_enter", True),
            global_delay_ms=self.settings.get("global_delay_ms", 120),
        )
        self._sync_tray_icon()
        self._append_log(
            "Settings updated: "
            f"default_auto_enter={'on' if self.settings.get('auto_enter', True) else 'off'}, "
            f"delay={int(self.settings.get('global_delay_ms', 120))}ms, "
            f"tray={'on' if self.settings.get('tray_enabled', True) else 'off'}, "
            f"minimize_to_tray={'on' if self.settings.get('minimize_to_tray', False) else 'off'}, "
            f"engine_auto_start={'on' if self.settings.get('engine_auto_start', False) else 'off'}"
        )
        self._refresh_rule_views()
        self._update_status()
        self._show_page("settings")
