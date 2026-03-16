from __future__ import annotations

import os
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem

from ..storage import save_rules
from .dialogs import DeleteRuleDialog, ToggleRuleDialog


class WindowRulesMixin:
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
            self.rule_preview.setPlainText("Select a rule to view its details.")
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

        rule = dict(self.rules[index])
        if not DeleteRuleDialog.confirm(self, rule):
            return

        trigger = str(rule.get("trigger", ""))
        self.rules.pop(index)
        self._append_log(f"Rule deleted: {trigger}")
        self._persist_and_refresh()
        self._clear_editor_form()

    def _toggle(self) -> None:
        index = self._selected_or_editor_index()
        if index is None:
            return

        rule = dict(self.rules[index])
        if not ToggleRuleDialog.confirm(self, rule):
            return

        rule["enabled"] = not bool(rule.get("enabled", True))
        self.rules[index] = rule
        state_label = "enabled" if rule["enabled"] else "disabled"
        self._append_log(f"Rule {state_label}: {rule.get('trigger', '')}")
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
