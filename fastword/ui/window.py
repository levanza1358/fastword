from __future__ import annotations

import ctypes
import os
import sys
from typing import Optional

from PyQt6.QtCore import QEvent, QObject, QTimer, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QDesktopServices, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..engine import FastWordEngine
from ..qt_theme import APP_STYLESHEET, STATUS_RUNNING, STATUS_STOPPED
from ..runtime import resource_path
from ..startup import is_enabled as is_startup_enabled
from ..startup import set_enabled as set_startup_enabled
from ..storage import (
    create_backup,
    data_dir,
    export_data,
    import_data,
    load_config,
    load_rules,
    rules_path,
    save_config,
    save_rules,
)
from .pages import (
    build_donate_page,
    build_editor_page,
    build_home_page,
    build_license_page,
    build_log_page,
    build_settings_page,
)

APP_NAME = "FastWord"
APP_MARK = "FW"
APP_DESKTOP_ID = "FastWord.Desktop"
APP_LICENSE_TEXT = """FastWord Proprietary License

Copyright (c) 2026 Rizqi Ismanda Nugraha
All rights reserved.

1. License Grant
You may install and use one or more copies of FastWord for personal or internal business use.

2. Restrictions
You may not redistribute, resell, sublicense, lease, modify, reverse engineer, or publish this software without prior written permission from the copyright holder.

3. Ownership
FastWord, its code, assets, branding, and related materials remain the exclusive property of Rizqi Ismanda Nugraha.

4. Donations
Donations support development and maintenance of the software. Donations do not transfer ownership, source code rights, or redistribution rights.

5. Warranty Disclaimer
This software is provided "as is" without warranties of any kind, express or implied.

6. Limitation of Liability
The author is not liable for any claim, damage, data loss, business interruption, or other liability arising from the use of this software.

7. Contact and Permission
For commercial licensing, redistribution, or modification requests, contact the copyright holder directly.
"""

BANK_NAME = "BCA"
BANK_ACCOUNT_NUMBER = "1710873620"
BANK_ACCOUNT_NAME = "Rizqi Ismanda Nugraha"
DEVELOPER_NAME = "Rizqi Ismanda Nugraha"
GITHUB_USERNAME = "@levanza1358"
GITHUB_URL = "https://github.com/levanza1358"
PAYPAL_URL = "https://paypal.me/rizqiismanda"
PAYPAL_DISPLAY_TEXT = "Send support directly to PayPal.me/rizqiismanda."


class LogBridge(QObject):
    message = pyqtSignal(str)


class FastWordWindow(QMainWindow):
    def __init__(self):
        self._quitting = False
        self._hidden_to_tray = False
        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._preview_pixmap: Optional[QPixmap] = None
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1260, 820)
        self.setMinimumSize(1080, 700)

        self.engine = FastWordEngine()
        self.log_bridge = LogBridge()
        self.log_bridge.message.connect(self._append_log)
        self.engine.log_callback = self.log_bridge.message.emit

        self.rules = load_rules()
        self.settings = load_config()
        self.settings["start_with_windows"] = is_startup_enabled()

        self.filtered_rule_indices: list[int] = []
        self.nav_buttons: dict[str, QPushButton] = {}
        self.page_index: dict[str, int] = {}
        self.editor_mode = "add"
        self.editor_rule_index: Optional[int] = None
        self.log_lines: list[str] = []
        self.license_text_value = APP_LICENSE_TEXT
        self.bank_name = BANK_NAME
        self.bank_account_number = BANK_ACCOUNT_NUMBER
        self.bank_account_name = BANK_ACCOUNT_NAME
        self.developer_name = DEVELOPER_NAME
        self.github_username = GITHUB_USERNAME
        self.github_url = GITHUB_URL
        self.paypal_url = PAYPAL_URL
        self.paypal_display_text = PAYPAL_DISPLAY_TEXT

        self.engine.set_rules(self.rules)
        self.engine.configure(
            auto_enter=self.settings.get("auto_enter", True),
            global_delay_ms=self.settings.get("global_delay_ms", 120),
        )

        self._apply_window_icon()
        self._build_shell()
        self._load_settings_into_form()
        self._refresh_rule_views()
        self._update_status()
        self._show_page("home")
        self._sync_tray_icon()
        QTimer.singleShot(0, self._auto_start_engine_if_needed)

    def _apply_window_icon(self) -> None:
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_DESKTOP_ID)
        except Exception:
            pass

        icon = QIcon()
        for candidate in (
            resource_path("assets", "app.ico"),
            resource_path("assets", "app.png"),
        ):
            if os.path.exists(candidate):
                icon = QIcon(candidate)
                if not icon.isNull():
                    break

        if not icon.isNull():
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)

    def _build_shell(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 18, 18, 18)
        sidebar_layout.setSpacing(16)

        brand_card = QFrame()
        brand_card.setObjectName("sidebarBrand")
        brand_layout = QVBoxLayout(brand_card)
        brand_layout.setContentsMargins(10, 6, 10, 6)
        brand_layout.setSpacing(10)

        brand = QLabel()
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFixedSize(48, 48)
        brand.setObjectName("brandIcon")
        brand_pixmap = QPixmap(resource_path("assets", "app.png"))
        if not brand_pixmap.isNull():
            brand.setPixmap(
                brand_pixmap.scaled(
                    48,
                    48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            brand.setText(APP_MARK)
            brand.setObjectName("brandMark")
        brand_layout.addWidget(brand, alignment=Qt.AlignmentFlag.AlignLeft)

        sidebar_title = QLabel(APP_NAME)
        sidebar_title.setObjectName("sidebarTitle")
        brand_layout.addWidget(sidebar_title)

        sidebar_subtitle = QLabel("Desktop text expander.")
        sidebar_subtitle.setObjectName("muted")
        sidebar_subtitle.setWordWrap(True)
        brand_layout.addWidget(sidebar_subtitle)

        self.sidebar_status_badge = QLabel("Engine Stopped")
        self.sidebar_status_badge.setObjectName("sidebarBadge")
        brand_layout.addWidget(self.sidebar_status_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        sidebar_layout.addWidget(brand_card)

        nav_group = QFrame()
        nav_group.setObjectName("navGroup")
        nav_layout = QVBoxLayout(nav_group)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(6)

        for key, label in (
            ("home", "Home"),
            ("editor", "Word Editor"),
            ("log", "Activity Log"),
            ("settings", "Settings"),
            ("license", "License"),
            ("donate", "Donate"),
        ):
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.clicked.connect(lambda _checked=False, page=key: self._show_page(page))
            nav_layout.addWidget(button)
            self.nav_buttons[key] = button

        sidebar_layout.addWidget(nav_group)
        sidebar_layout.addStretch(1)

        storage_card = QFrame()
        storage_card.setObjectName("storageCard")
        storage_layout = QVBoxLayout(storage_card)
        storage_layout.setContentsMargins(4, 8, 4, 0)
        storage_layout.setSpacing(6)

        storage_label = QLabel("Rules Storage")
        storage_label.setObjectName("sidebarKicker")
        storage_layout.addWidget(storage_label)

        storage_path_label = QLabel(rules_path())
        storage_path_label.setObjectName("pathText")
        storage_path_label.setWordWrap(True)
        storage_layout.addWidget(storage_path_label)
        sidebar_layout.addWidget(storage_card)

        content = QWidget()
        content.setObjectName("contentRoot")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(0)

        self.pages = QStackedWidget()
        self.pages.addWidget(build_home_page(self))
        self.page_index["home"] = 0
        self.pages.addWidget(build_editor_page(self))
        self.page_index["editor"] = 1
        self.pages.addWidget(build_log_page(self))
        self.page_index["log"] = 2
        self.pages.addWidget(build_settings_page(self))
        self.page_index["settings"] = 3
        self.pages.addWidget(build_license_page(self))
        self.page_index["license"] = 4
        self.pages.addWidget(build_donate_page(self))
        self.page_index["donate"] = 5
        content_layout.addWidget(self.pages)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(content, 1)
        self.setCentralWidget(root)

    def _show_page(self, page_name: str) -> None:
        if page_name not in self.page_index:
            return
        if page_name == "settings":
            self._load_settings_into_form()
        self.pages.setCurrentIndex(self.page_index[page_name])
        for key, button in self.nav_buttons.items():
            button.setProperty("active", key == page_name)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

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

    def _copy_bank_account_number(self) -> None:
        self._copy_to_clipboard(self.bank_account_number, "Bank account number")

    def _copy_bank_account_name(self) -> None:
        self._copy_to_clipboard(self.bank_account_name, "Bank account name")

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

    def _refresh_rule_views(self) -> None:
        total = len(self.rules)
        active = 0
        enter_on = 0
        default_auto_enter = bool(self.settings.get("auto_enter", True))
        keyword = self.search_edit.text().strip().lower()
        mode = self.filter_combo.currentText().strip() or "all"
        preferred_index = self._selected_or_editor_index()

        self.filtered_rule_indices = []
        self.rule_table.blockSignals(True)
        self.rule_table.setRowCount(0)

        for index, rule in enumerate(self.rules):
            trigger = str(rule.get("trigger", ""))
            replacement = str(rule.get("replacement", ""))
            enabled = bool(rule.get("enabled", True))
            auto_enter = bool(rule.get("auto_enter", default_auto_enter))
            image_path = str(rule.get("image_path", "")).strip()
            app_targets = ", ".join(rule.get("app_targets", []) or [])

            if enabled:
                active += 1
            if auto_enter:
                enter_on += 1

            searchable = " ".join(
                [trigger.lower(), replacement.lower(), image_path.lower(), app_targets.lower()]
            )
            if keyword and keyword not in searchable:
                continue
            if mode == "active" and not enabled:
                continue
            if mode == "inactive" and enabled:
                continue
            if mode == "auto_enter_on" and not auto_enter:
                continue
            if mode == "auto_enter_off" and auto_enter:
                continue
            if mode == "has_image" and not image_path:
                continue
            if mode == "text_only" and image_path:
                continue

            row = self.rule_table.rowCount()
            self.rule_table.insertRow(row)
            self.filtered_rule_indices.append(index)

            output_text = replacement.replace("\r\n", "\n").replace("\n", " / ")
            if len(output_text) > 140:
                output_text = output_text[:140] + "..."

            values = [
                QTableWidgetItem(trigger),
                QTableWidgetItem("Active" if enabled else "Off"),
                QTableWidgetItem("On" if auto_enter else "Off"),
                QTableWidgetItem(output_text),
            ]
            values[1].setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
            values[2].setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
            for column, item in enumerate(values):
                self.rule_table.setItem(row, column, item)

        self.rule_table.blockSignals(False)

        self.home_total.setText(str(total))
        self.home_active.setText(str(active))
        self.home_enter.setText(str(enter_on))
        self.editor_summary.setText(f"Showing {len(self.filtered_rule_indices)} of {total} rules")

        if preferred_index is not None and preferred_index in self.filtered_rule_indices:
            self.rule_table.selectRow(self.filtered_rule_indices.index(preferred_index))
        else:
            self.rule_table.clearSelection()

        if self.editor_mode == "edit" and self.editor_rule_index is not None and 0 <= self.editor_rule_index < len(self.rules):
            self._load_rule_into_editor(self.editor_rule_index, preserve_selection=True)
        self._update_rule_preview()
        self._update_status()

    def _selected_index(self) -> Optional[int]:
        selected_rows = self.rule_table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        if 0 <= row < len(self.filtered_rule_indices):
            return self.filtered_rule_indices[row]
        return None

    def _selected_or_editor_index(self) -> Optional[int]:
        selected_index = self._selected_index()
        if selected_index is not None:
            return selected_index
        if self.editor_mode == "edit" and self.editor_rule_index is not None:
            if 0 <= self.editor_rule_index < len(self.rules):
                return self.editor_rule_index
        return None

    def _update_rule_preview(self) -> None:
        index = self._selected_index()
        if index is not None:
            self._load_rule_into_editor(index, preserve_selection=True)
        else:
            index = self._selected_or_editor_index()

        if index is None or not (0 <= index < len(self.rules)):
            self.rule_preview.setPlainText(
                "Select a rule to view its details."
            )
            return

        rule = self.rules[index]
        self.rule_preview.setPlainText(
            "\n".join(
                [
                    f"Trigger   : {rule.get('trigger', '')}",
                    f"Enabled   : {'Yes' if rule.get('enabled', True) else 'No'}",
                    f"AutoEnter : {'Yes' if rule.get('auto_enter', self.settings.get('auto_enter', True)) else 'No'}",
                    f"Apps      : {', '.join(rule.get('app_targets', []) or []) or 'Global'}",
                    f"ImagePath : {rule.get('image_path', '') or '-'}",
                    "",
                    "Output:",
                    str(rule.get("replacement", "")) or "-",
                ]
            )
        )

    def _add(self) -> None:
        self._clear_editor_form()
        self._show_page("editor")

    def _delete(self) -> None:
        index = self._selected_or_editor_index()
        if index is None:
            return

        trigger = str(self.rules[index].get("trigger", ""))
        if (
            QMessageBox.question(
                self,
                "Delete Rule",
                f"Delete rule '{trigger}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.rules.pop(index)
        self._persist_and_refresh()
        self._clear_editor_form()

    def _toggle(self) -> None:
        index = self._selected_or_editor_index()
        if index is None:
            return

        rule = dict(self.rules[index])
        rule["enabled"] = not bool(rule.get("enabled", True))
        self.rules[index] = rule
        self._persist_and_refresh(select_index=index)

    def _persist_and_refresh(self, select_index: Optional[int] = None) -> None:
        save_rules(self.rules)
        self.engine.set_rules(self.rules)
        if select_index is not None and select_index >= len(self.rules):
            select_index = None
        if select_index is not None:
            self.editor_mode = "edit"
            self.editor_rule_index = select_index
        self._refresh_rule_views()

    def _browse_rule_image(self) -> None:
        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)",
        )
        if path:
            self.rule_image_edit.setText(path)

    def _update_image_preview(self) -> None:
        path = self.rule_image_edit.text().strip()
        if not path:
            self._preview_pixmap = None
            self.image_preview_label.setPixmap(QPixmap())
            self.image_preview_label.setText("Image preview will appear here")
            return

        if not os.path.exists(path):
            self._preview_pixmap = None
            self.image_preview_label.setPixmap(QPixmap())
            self.image_preview_label.setText("Image not found")
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._preview_pixmap = None
            self.image_preview_label.setPixmap(QPixmap())
            self.image_preview_label.setText(os.path.basename(path))
            return

        self._preview_pixmap = pixmap.scaled(
            280,
            140,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_preview_label.setText("")
        self.image_preview_label.setPixmap(self._preview_pixmap)

    def _clear_editor_form(self) -> None:
        self.editor_mode = "add"
        self.editor_rule_index = None
        self.editor_mode_label.setText("Create a new rule")
        self.rule_trigger_edit.clear()
        self.rule_apps_edit.clear()
        self.rule_output_edit.clear()
        self.rule_image_edit.clear()
        self.rule_enabled_check.setChecked(True)
        self.rule_auto_enter_check.setChecked(bool(self.settings.get("auto_enter", True)))
        self.rule_table.clearSelection()
        self._update_rule_preview()

    def _load_rule_into_editor(self, index: int, preserve_selection: bool = False) -> None:
        if not (0 <= index < len(self.rules)):
            return

        rule = self.rules[index]
        self.editor_mode = "edit"
        self.editor_rule_index = index
        self.editor_mode_label.setText(f"Editing: {rule.get('trigger', '')}")
        self.rule_trigger_edit.setText(str(rule.get("trigger", "")))
        self.rule_apps_edit.setText(", ".join(rule.get("app_targets", []) or []))
        self.rule_output_edit.setPlainText(str(rule.get("replacement", "")))
        self.rule_image_edit.setText(str(rule.get("image_path", "")))
        self.rule_enabled_check.setChecked(bool(rule.get("enabled", True)))
        self.rule_auto_enter_check.setChecked(bool(rule.get("auto_enter", self.settings.get("auto_enter", True))))
        self._update_image_preview()

        if not preserve_selection and index in self.filtered_rule_indices:
            self.rule_table.selectRow(self.filtered_rule_indices.index(index))

    def _save_editor_rule(self) -> None:
        trigger = self.rule_trigger_edit.text().strip()
        replacement = self.rule_output_edit.toPlainText()
        image_path = self.rule_image_edit.text().strip()
        enabled = self.rule_enabled_check.isChecked()
        auto_enter = self.rule_auto_enter_check.isChecked()
        app_targets = self._parse_app_targets(self.rule_apps_edit.text())

        if not trigger:
            QMessageBox.critical(self, "Invalid Rule", "Trigger cannot be empty.")
            return

        conflict = self._find_trigger_conflict(
            trigger,
            app_targets,
            self.editor_rule_index if self.editor_mode == "edit" else None,
        )
        if conflict:
            QMessageBox.critical(self, "Duplicate Trigger", conflict)
            return

        rule = {
            "trigger": trigger,
            "replacement": replacement,
            "image_path": image_path,
            "enabled": enabled,
            "auto_enter": auto_enter,
            "app_targets": app_targets,
        }

        if self.editor_mode == "edit" and self.editor_rule_index is not None and 0 <= self.editor_rule_index < len(self.rules):
            self.rules[self.editor_rule_index] = rule
            self._append_log(f"Rule updated: {trigger}")
            select_index = self.editor_rule_index
        else:
            self.rules.append(rule)
            self.editor_rule_index = len(self.rules) - 1
            self.editor_mode = "edit"
            self._append_log(f"Rule added: {trigger}")
            select_index = self.editor_rule_index

        self._persist_and_refresh(select_index=select_index)
        if select_index is not None:
            self._load_rule_into_editor(select_index, preserve_selection=True)

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

    def _auto_start_engine_if_needed(self) -> None:
        if not bool(self.settings.get("engine_auto_start", False)):
            return
        self._append_log("Auto starting engine on app launch")
        self._start()

    def _parse_app_targets(self, text: str) -> list[str]:
        targets: list[str] = []
        for part in (text or "").split(","):
            candidate = os.path.basename(part.strip()).lower()
            if candidate and candidate not in targets:
                targets.append(candidate)
        return targets

    def _find_trigger_conflict(self, trigger: str, app_targets: list[str], skip_index: Optional[int]) -> str | None:
        new_targets = set(app_targets)
        for index, rule in enumerate(self.rules):
            if skip_index is not None and index == skip_index:
                continue
            if str(rule.get("trigger", "")).strip() != trigger:
                continue
            existing_targets = set(rule.get("app_targets", []) or [])
            overlap = not existing_targets or not new_targets or bool(existing_targets & new_targets)
            if not overlap:
                continue
            if existing_targets:
                return (
                    f"Trigger '{trigger}' already exists for app targets: "
                    f"{', '.join(sorted(existing_targets))}."
                )
            return f"Trigger '{trigger}' already exists as a global rule."
        return None

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


class FastWordGUI:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setQuitOnLastWindowClosed(True)
        self.app.setStyleSheet(APP_STYLESHEET)
        self.window = FastWordWindow()

    def run(self):
        self.window.show()
        return self.app.exec()
