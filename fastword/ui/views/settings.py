from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..components import create_card


def build_settings_page(window) -> QWidget:
    page = QWidget()
    page.setObjectName("pageRoot")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)

    hero = create_card("heroCard")
    hero_layout = QVBoxLayout(hero)
    hero_layout.setContentsMargins(22, 22, 22, 22)
    hero_layout.setSpacing(6)

    title = QLabel("Settings")
    title.setObjectName("heroTitle")
    hero_layout.addWidget(title)

    subtitle = QLabel("Manage app behavior, tray options, startup mode, and backups.")
    subtitle.setObjectName("muted")
    subtitle.setWordWrap(True)
    hero_layout.addWidget(subtitle)
    layout.addWidget(hero)

    body = QVBoxLayout()
    body.setSpacing(12)

    panel = create_card()
    panel_layout = QVBoxLayout(panel)
    panel_layout.setContentsMargins(20, 20, 20, 20)
    panel_layout.setSpacing(12)

    panel_title = QLabel("App Settings")
    panel_title.setObjectName("sectionTitle")
    panel_layout.addWidget(panel_title)

    panel_note = QLabel("Changes apply after you save.")
    panel_note.setObjectName("muted")
    panel_note.setWordWrap(True)
    panel_layout.addWidget(panel_note)

    options_grid = QGridLayout()
    options_grid.setHorizontalSpacing(24)
    options_grid.setVerticalSpacing(10)

    window.settings_auto_enter_check = QCheckBox("Default Auto Enter for new rules")
    options_grid.addWidget(window.settings_auto_enter_check, 0, 0)

    window.settings_tray_enabled_check = QCheckBox("Enable system tray")
    window.settings_tray_enabled_check.toggled.connect(window._sync_minimize_checkbox_state)
    options_grid.addWidget(window.settings_tray_enabled_check, 0, 1)

    window.settings_minimize_to_tray_check = QCheckBox("Minimize to tray")
    options_grid.addWidget(window.settings_minimize_to_tray_check, 1, 0)

    window.settings_startup_check = QCheckBox("Start with Windows")
    options_grid.addWidget(window.settings_startup_check, 1, 1)

    window.settings_engine_auto_start_check = QCheckBox("Auto start engine when app opens")
    options_grid.addWidget(window.settings_engine_auto_start_check, 2, 0, 1, 2)
    panel_layout.addLayout(options_grid)

    close_note = QLabel("Window close always exits the app. Close-to-tray has been removed.")
    close_note.setObjectName("fieldLabel")
    close_note.setWordWrap(True)
    panel_layout.addWidget(close_note)

    delay_row = QHBoxLayout()
    delay_row.setSpacing(10)

    delay_label = QLabel("Global delay before Enter (ms)")
    delay_label.setObjectName("fieldLabel")
    delay_row.addWidget(delay_label)

    window.settings_delay_spin = QSpinBox()
    window.settings_delay_spin.setRange(0, 60000)
    window.settings_delay_spin.setSingleStep(10)
    delay_row.addWidget(window.settings_delay_spin, 1)
    panel_layout.addLayout(delay_row)

    action_grid = QGridLayout()
    action_grid.setHorizontalSpacing(8)
    action_grid.setVerticalSpacing(8)

    save_button = QPushButton("Save Settings")
    save_button.setObjectName("primaryButton")
    save_button.clicked.connect(window._save_settings_page)
    action_grid.addWidget(save_button, 0, 0)

    reset_button = QPushButton("Reset Form")
    reset_button.clicked.connect(window._load_settings_into_form)
    action_grid.addWidget(reset_button, 0, 1)

    open_rules_button = QPushButton("Open Rules File")
    open_rules_button.clicked.connect(window._open_rules)
    action_grid.addWidget(open_rules_button, 0, 2)

    open_data_button = QPushButton("Open Data Folder")
    open_data_button.clicked.connect(window._open_data_dir)
    action_grid.addWidget(open_data_button, 0, 3)

    export_button = QPushButton("Export Backup")
    export_button.clicked.connect(window._export_backup)
    action_grid.addWidget(export_button, 1, 0)

    import_button = QPushButton("Import Backup")
    import_button.clicked.connect(window._import_backup)
    action_grid.addWidget(import_button, 1, 1)
    panel_layout.addLayout(action_grid)
    panel_layout.addStretch(1)

    summary = create_card()
    summary_layout = QVBoxLayout(summary)
    summary_layout.setContentsMargins(20, 20, 20, 20)
    summary_layout.setSpacing(10)

    summary_title = QLabel("Summary")
    summary_title.setObjectName("sectionTitle")
    summary_layout.addWidget(summary_title)

    window.settings_summary = QLabel("")
    window.settings_summary.setObjectName("muted")
    window.settings_summary.setWordWrap(True)
    summary_layout.addWidget(window.settings_summary)

    for note in (
        "Existing rules keep their own Auto Enter setting.",
        "Default Auto Enter only applies to newly created rules.",
        "Global delay applies every time the app sends Enter after content injection.",
    ):
        label = QLabel(note)
        label.setObjectName("listItem")
        label.setWordWrap(True)
        summary_layout.addWidget(label)
    summary_layout.addStretch(1)

    body.addWidget(panel)
    body.addWidget(summary)
    layout.addLayout(body, 1)
    return page
