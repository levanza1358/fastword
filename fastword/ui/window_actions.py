from __future__ import annotations

import os

from PyQt6.QtCore import QEvent, QTimer, QUrl
from PyQt6.QtGui import QAction, QCloseEvent, QDesktopServices
from PyQt6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox, QSystemTrayIcon

from ..app_info import APP_NAME
from ..qt_theme import STATUS_RUNNING, STATUS_STOPPED
from ..startup import set_enabled as set_startup_enabled
from ..storage import (
    create_backup,
    data_dir,
    export_data,
    import_data,
    rules_path,
    save_config,
    save_rules,
)


class WindowActionsMixin:
    def _append_log(self, message: str) -> None:
        self.log_lines.append(message)
        self.log_text.appendPlainText(message)

    def _clear_log(self) -> None:
        self.log_lines.clear()
        self.log_text.clear()

    def _copy_log(self) -> None:
        QApplication.clipboard().setText("\n".join(self.log_lines))
        self._append_log("Log copied to clipboard")

    def _copy_to_clipboard(self, text: str, label: str) -> None:
        QApplication.clipboard().setText(text)
        self._append_log(f"{label} copied to clipboard")

    def _copy_license_text(self) -> None:
        self._copy_to_clipboard(self.license_text_value, "License text")

    def _copy_github_link(self) -> None:
        self._copy_to_clipboard(self.github_url, "GitHub link")

    def _copy_paypal_link(self) -> None:
        if not self.paypal_url:
            QMessageBox.information(self, "PayPal", "PayPal link is not configured yet.")
            return
        self._copy_to_clipboard(self.paypal_url, "PayPal link")

    def _open_paypal_link(self) -> None:
        if not self.paypal_url:
            QMessageBox.information(
                self,
                "PayPal",
                "PayPal link is not configured yet. Add your PayPal.me link or PayPal email in the app constants.",
            )
            return
        if not QDesktopServices.openUrl(QUrl(self.paypal_url)):
            QMessageBox.critical(self, "PayPal", "Failed to open the PayPal link.")

    def _open_github_link(self) -> None:
        if not QDesktopServices.openUrl(QUrl(self.github_url)):
            QMessageBox.critical(self, "GitHub", "Failed to open the GitHub link.")

    def _start(self) -> None:
        self.engine.set_rules(self.rules)
        self.engine.start()
        self._update_status()

    def _stop(self) -> None:
        self.engine.stop()
        self._update_status()

    def _update_status(self) -> None:
        running = self.engine.running
        default_auto_enter = "ON" if self.settings.get("auto_enter", True) else "OFF"
        tray_enabled = bool(self.settings.get("tray_enabled", True))
        tray_text = "ON" if tray_enabled else "OFF"
        if tray_enabled and not QSystemTrayIcon.isSystemTrayAvailable():
            tray_text = "Unavailable"
        minimize_text = "ON" if self.settings.get("minimize_to_tray", False) and tray_enabled else "OFF"
        startup_text = "ON" if self.settings.get("start_with_windows", False) else "OFF"
        engine_auto_start_text = "ON" if self.settings.get("engine_auto_start", False) else "OFF"
        delay_ms = int(self.settings.get("global_delay_ms", 120))

        self.sidebar_status_badge.setText("Engine Running" if running else "Engine Stopped")
        self.sidebar_status_badge.setStyleSheet(STATUS_RUNNING if running else STATUS_STOPPED)
        self.settings_summary.setText(
            f"Default Auto Enter: {default_auto_enter}\n"
            f"Global Delay: {delay_ms} ms\n"
            f"System Tray: {tray_text}\n"
            f"Minimize to Tray: {minimize_text}\n"
            f"Start with Windows: {startup_text}\n"
            f"Engine Auto Start: {engine_auto_start_text}\n"
            "Close Action: exit app"
        )

    def _auto_start_engine_if_needed(self) -> None:
        if not bool(self.settings.get("engine_auto_start", False)):
            return
        self._append_log("Auto starting engine on app launch")
        self._start()

    def _open_path(self, path: str) -> None:
        try:
            os.startfile(path)
        except AttributeError:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception:
            raise

    def _open_data_dir(self) -> None:
        try:
            self._open_path(data_dir())
        except Exception:
            QMessageBox.critical(self, "Open Data Folder", "Failed to open the data folder.")

    def _export_backup(self) -> None:
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Backup",
            "fastword-backup.json",
            "JSON Files (*.json);;All Files (*.*)",
        )
        if not path:
            return
        export_data(path, self.rules, self.settings)
        self._append_log(f"Backup exported: {path}")

    def _import_backup(self) -> None:
        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Import Backup",
            "",
            "JSON Files (*.json);;All Files (*.*)",
        )
        if not path:
            return

        try:
            backup_path = create_backup(self.rules, self.settings)
            data = import_data(path)
            self.rules = data["rules"]
            self.settings = data["settings"]
            set_startup_enabled(self.settings.get("start_with_windows", False))
            save_config(self.settings)
            save_rules(self.rules)
            self.engine.set_rules(self.rules)
            self.engine.configure(
                auto_enter=self.settings.get("auto_enter", True),
                global_delay_ms=self.settings.get("global_delay_ms", 120),
            )
            self._sync_tray_icon()
            self._load_settings_into_form()
            self._clear_editor_form()
            self._refresh_rule_views()
            self._update_status()
            self._append_log(f"Backup imported: {path}")
            self._append_log(f"Pre-import backup created: {backup_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Import Failed", str(exc))

    def _open_rules(self) -> None:
        try:
            self._open_path(rules_path())
        except Exception:
            QMessageBox.critical(self, "Open rules.json", "Failed to open rules.json.")

    def _ensure_tray_icon(self) -> None:
        if self._tray_icon is not None:
            return

        self._tray_icon = QSystemTrayIcon(self.windowIcon(), self)
        self._tray_icon.setToolTip(APP_NAME)
        self._tray_icon.activated.connect(self._handle_tray_activation)

        menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(self._restore_from_tray)
        menu.addAction(show_action)

        start_action = QAction("Start Engine", self)
        start_action.triggered.connect(self._start)
        menu.addAction(start_action)

        stop_action = QAction("Stop Engine", self)
        stop_action.triggered.connect(self._stop)
        menu.addAction(stop_action)

        menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._quit_app)
        menu.addAction(exit_action)
        self._tray_icon.setContextMenu(menu)

    def _sync_tray_icon(self) -> None:
        enabled = bool(self.settings.get("tray_enabled", True)) and QSystemTrayIcon.isSystemTrayAvailable()
        if enabled:
            self._ensure_tray_icon()
            self._tray_icon.show()
        elif self._tray_icon is not None:
            self._tray_icon.hide()
            if self._hidden_to_tray:
                self._restore_from_tray()

        self._sync_minimize_checkbox_state()

    def _handle_tray_activation(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self._restore_from_tray()

    def _hide_to_tray(self) -> None:
        if not bool(self.settings.get("tray_enabled", True)):
            return
        if not bool(self.settings.get("minimize_to_tray", False)):
            return
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self._ensure_tray_icon()
        self._tray_icon.show()
        self._hidden_to_tray = True
        self.hide()
        self._tray_icon.showMessage(
            APP_NAME,
            "The window was minimized to the system tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2500,
        )

    def _restore_from_tray(self) -> None:
        self._hidden_to_tray = False
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _quit_app(self) -> None:
        self._shutdown()
        QApplication.instance().quit()

    def _shutdown(self) -> None:
        if self._quitting:
            return
        self._quitting = True
        self.engine.log_callback = None
        try:
            self.engine.stop()
        except Exception:
            pass
        if self._tray_icon is not None:
            self._tray_icon.hide()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if self._quitting:
            return
        if event.type() != QEvent.Type.WindowStateChange:
            return
        if self.isMinimized() and self.settings.get("tray_enabled", True) and self.settings.get("minimize_to_tray", False):
            QTimer.singleShot(0, self._hide_to_tray)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._shutdown()
        event.accept()
