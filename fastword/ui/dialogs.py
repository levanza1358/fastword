from __future__ import annotations

import math
import time

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .components import create_card


class DeleteRuleDialog(QDialog):
    def __init__(self, parent: QWidget | None, rule: dict):
        super().__init__(parent)
        self.rule = dict(rule or {})
        self.trigger = str(self.rule.get("trigger", "")).strip()
        self._unlock_deadline = time.monotonic() + 1.0
        self._unlock_ready = False

        self.setWindowTitle("Delete Rule")
        self.setModal(True)
        self.setMinimumWidth(540)
        self.resize(560, 420)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        hero = create_card("heroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(6)

        title = QLabel("Delete Rule")
        title.setObjectName("heroTitle")
        hero_layout.addWidget(title)

        subtitle = QLabel("Review the selected rule before removing it. This action cannot be undone.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(subtitle)
        root.addWidget(hero)

        warning = create_card("dangerCard")
        warning_layout = QVBoxLayout(warning)
        warning_layout.setContentsMargins(18, 16, 18, 16)
        warning_layout.setSpacing(6)

        warning_title = QLabel("Permanent Action")
        warning_title.setObjectName("dangerTitle")
        warning_layout.addWidget(warning_title)

        warning_text = QLabel("Deleting this rule removes its trigger, output, image path, and app targeting setup.")
        warning_text.setObjectName("dangerText")
        warning_text.setWordWrap(True)
        warning_layout.addWidget(warning_text)
        root.addWidget(warning)

        summary = create_card()
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(18, 18, 18, 18)
        summary_layout.setSpacing(10)

        trigger_label = QLabel(f"Trigger: {self.trigger or '-'}")
        trigger_label.setObjectName("sectionTitle")
        summary_layout.addWidget(trigger_label)

        apps = ", ".join(self.rule.get("app_targets", []) or []) or "Global"
        apps_label = QLabel(f"Apps: {apps}")
        apps_label.setObjectName("fieldLabel")
        apps_label.setWordWrap(True)
        summary_layout.addWidget(apps_label)

        auto_enter = "On" if self.rule.get("auto_enter", False) else "Off"
        enabled = "Yes" if self.rule.get("enabled", True) else "No"
        meta_label = QLabel(f"Enabled: {enabled} | Auto Enter: {auto_enter}")
        meta_label.setObjectName("fieldLabel")
        meta_label.setWordWrap(True)
        summary_layout.addWidget(meta_label)

        image_path = str(self.rule.get("image_path", "") or "").strip() or "-"
        image_label = QLabel(f"Image: {image_path}")
        image_label.setObjectName("muted")
        image_label.setWordWrap(True)
        summary_layout.addWidget(image_label)

        output_title = QLabel("Output Preview")
        output_title.setObjectName("fieldLabel")
        summary_layout.addWidget(output_title)

        output_preview = QPlainTextEdit()
        output_preview.setObjectName("previewBox")
        output_preview.setReadOnly(True)
        output_preview.setMinimumHeight(120)
        output_preview.setPlainText(str(self.rule.get("replacement", "") or "-"))
        summary_layout.addWidget(output_preview)
        root.addWidget(summary)

        confirm = create_card()
        confirm_layout = QVBoxLayout(confirm)
        confirm_layout.setContentsMargins(18, 18, 18, 18)
        confirm_layout.setSpacing(10)

        confirm_label = QLabel(f"Type {self.trigger or 'the trigger'} to confirm deletion")
        confirm_label.setObjectName("fieldLabel")
        confirm_label.setWordWrap(True)
        confirm_layout.addWidget(confirm_label)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText(self.trigger or "Type the trigger")
        self.confirm_input.textChanged.connect(self._sync_delete_button_state)
        confirm_layout.addWidget(self.confirm_input)

        self.confirm_status = QLabel("Waiting for confirmation...")
        self.confirm_status.setObjectName("muted")
        self.confirm_status.setWordWrap(True)
        confirm_layout.addWidget(self.confirm_status)
        root.addWidget(confirm)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        action_row.addStretch(1)

        cancel_button = QPushButton("Cancel")
        cancel_button.setDefault(True)
        cancel_button.clicked.connect(self.reject)
        action_row.addWidget(cancel_button)

        self.delete_button = QPushButton("Delete Rule")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.setEnabled(False)
        self.delete_button.setAutoDefault(False)
        self.delete_button.clicked.connect(self.accept)
        action_row.addWidget(self.delete_button)
        root.addLayout(action_row)

        self._unlock_timer = QTimer(self)
        self._unlock_timer.setInterval(100)
        self._unlock_timer.timeout.connect(self._tick_unlock_timer)
        self._unlock_timer.start()
        QTimer.singleShot(0, self.confirm_input.setFocus)
        self._tick_unlock_timer()

    def _sync_delete_button_state(self) -> None:
        typed = self.confirm_input.text().strip()
        matches = typed == self.trigger
        self.delete_button.setEnabled(matches and self._unlock_ready)

        if not matches:
            self.confirm_status.setText("Type the exact trigger to enable deletion.")
        elif not self._unlock_ready:
            self.confirm_status.setText("Confirmation matched. Waiting for safety delay...")
        else:
            self.confirm_status.setText("Ready to delete this rule.")

    def _tick_unlock_timer(self) -> None:
        remaining = self._unlock_deadline - time.monotonic()
        if remaining <= 0:
            self._unlock_ready = True
            self._unlock_timer.stop()
            self.delete_button.setText("Delete Rule")
            self._sync_delete_button_state()
            return

        seconds = max(1, math.ceil(remaining))
        self.delete_button.setText(f"Delete Rule ({seconds}s)")
        self._sync_delete_button_state()

    @classmethod
    def confirm(cls, parent: QWidget | None, rule: dict) -> bool:
        dialog = cls(parent, rule)
        return dialog.exec() == int(QDialog.DialogCode.Accepted)


class ToggleRuleDialog(QDialog):
    def __init__(self, parent: QWidget | None, rule: dict):
        super().__init__(parent)
        self.rule = dict(rule or {})
        self.trigger = str(self.rule.get("trigger", "")).strip()
        self.next_enabled = not bool(self.rule.get("enabled", True))
        self._unlock_deadline = time.monotonic() + 0.8
        self._unlock_ready = False

        self.setWindowTitle("Toggle Rule")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.resize(520, 340)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        hero = create_card("heroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(6)

        title = QLabel("Toggle Rule")
        title.setObjectName("heroTitle")
        hero_layout.addWidget(title)

        action_text = "enable" if self.next_enabled else "disable"
        subtitle = QLabel(f"You are about to {action_text} this rule.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(subtitle)
        root.addWidget(hero)

        summary = create_card()
        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(18, 18, 18, 18)
        summary_layout.setSpacing(10)

        trigger_label = QLabel(f"Trigger: {self.trigger or '-'}")
        trigger_label.setObjectName("sectionTitle")
        summary_layout.addWidget(trigger_label)

        current_status = "Active" if self.rule.get("enabled", True) else "Off"
        next_status = "Active" if self.next_enabled else "Off"
        status_label = QLabel(f"Status: {current_status} -> {next_status}")
        status_label.setObjectName("fieldLabel")
        summary_layout.addWidget(status_label)

        apps = ", ".join(self.rule.get("app_targets", []) or []) or "Global"
        apps_label = QLabel(f"Apps: {apps}")
        apps_label.setObjectName("fieldLabel")
        apps_label.setWordWrap(True)
        summary_layout.addWidget(apps_label)

        output_preview = QPlainTextEdit()
        output_preview.setObjectName("previewBox")
        output_preview.setReadOnly(True)
        output_preview.setMinimumHeight(100)
        output_preview.setPlainText(str(self.rule.get("replacement", "") or "-"))
        summary_layout.addWidget(output_preview)
        root.addWidget(summary)

        self.status_hint = QLabel("Preparing action...")
        self.status_hint.setObjectName("muted")
        self.status_hint.setWordWrap(True)
        root.addWidget(self.status_hint)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        action_row.addStretch(1)

        cancel_button = QPushButton("Cancel")
        cancel_button.setDefault(True)
        cancel_button.clicked.connect(self.reject)
        action_row.addWidget(cancel_button)

        self.apply_button = QPushButton("Apply")
        self.apply_button.setObjectName("primaryButton" if self.next_enabled else "dangerButton")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.accept)
        action_row.addWidget(self.apply_button)
        root.addLayout(action_row)

        self._unlock_timer = QTimer(self)
        self._unlock_timer.setInterval(100)
        self._unlock_timer.timeout.connect(self._tick_unlock_timer)
        self._unlock_timer.start()
        self._tick_unlock_timer()

    def _tick_unlock_timer(self) -> None:
        remaining = self._unlock_deadline - time.monotonic()
        if remaining <= 0:
            self._unlock_ready = True
            self._unlock_timer.stop()
            self.apply_button.setEnabled(True)
            self.apply_button.setText("Enable Rule" if self.next_enabled else "Disable Rule")
            self.status_hint.setText("Ready to apply this change.")
            return

        seconds = max(1, math.ceil(remaining))
        label = "Enable Rule" if self.next_enabled else "Disable Rule"
        self.apply_button.setText(f"{label} ({seconds}s)")
        self.status_hint.setText("Reviewing selected rule...")

    @classmethod
    def confirm(cls, parent: QWidget | None, rule: dict) -> bool:
        dialog = cls(parent, rule)
        return dialog.exec() == int(QDialog.DialogCode.Accepted)
