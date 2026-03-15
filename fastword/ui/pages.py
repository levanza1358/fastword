from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from .components import create_card, create_panel, create_stat_card


def build_home_page(window) -> QWidget:
    page = QWidget()
    page.setObjectName("pageRoot")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)

    hero = create_card("heroCard")
    hero_layout = QGridLayout(hero)
    hero_layout.setContentsMargins(20, 18, 20, 18)
    hero_layout.setHorizontalSpacing(16)
    hero_layout.setVerticalSpacing(6)

    hero_title = QLabel("Home")
    hero_title.setObjectName("heroTitle")
    hero_layout.addWidget(hero_title, 0, 0)
    hero_layout.setColumnStretch(0, 1)

    action_row = QHBoxLayout()
    action_row.setSpacing(8)

    start_button = QPushButton("Start Engine")
    start_button.setObjectName("primaryButton")
    start_button.clicked.connect(window._start)
    action_row.addWidget(start_button)

    stop_button = QPushButton("Stop")
    stop_button.clicked.connect(window._stop)
    action_row.addWidget(stop_button)

    settings_button = QPushButton("Open Settings")
    settings_button.clicked.connect(lambda: window._show_page("settings"))
    action_row.addWidget(settings_button)

    hero_layout.addLayout(
        action_row,
        0,
        1,
        1,
        1,
        alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
    )
    layout.addWidget(hero)

    stats_row = QHBoxLayout()
    stats_row.setSpacing(12)
    total_card, window.home_total = create_stat_card("Rules", "Saved triggers ready for use")
    active_card, window.home_active = create_stat_card("Active", "Enabled automations in the library")
    enter_card, window.home_enter = create_stat_card("Auto Enter", "Rules that submit immediately")
    stats_row.addWidget(total_card)
    stats_row.addWidget(active_card)
    stats_row.addWidget(enter_card)
    layout.addLayout(stats_row)

    lower = QHBoxLayout()
    lower.setSpacing(12)

    quick = create_card()
    quick_layout = QVBoxLayout(quick)
    quick_layout.setContentsMargins(18, 18, 18, 18)
    quick_layout.setSpacing(10)
    quick_title = QLabel("Shortcuts")
    quick_title.setObjectName("sectionTitle")
    quick_layout.addWidget(quick_title)

    new_button = QPushButton("Create Rule")
    new_button.setObjectName("primaryButton")
    new_button.clicked.connect(window._add)
    quick_layout.addWidget(new_button)

    editor_button = QPushButton("Open Word Editor")
    editor_button.clicked.connect(lambda: window._show_page("editor"))
    quick_layout.addWidget(editor_button)

    github_button = QPushButton(f"Developer GitHub {window.github_username}")
    github_button.clicked.connect(window._open_github_link)
    quick_layout.addWidget(github_button)

    log_button = QPushButton("Open Log")
    log_button.clicked.connect(lambda: window._show_page("log"))
    quick_layout.addWidget(log_button)
    quick_layout.addStretch(1)

    notes = create_card()
    notes_layout = QVBoxLayout(notes)
    notes_layout.setContentsMargins(18, 18, 18, 18)
    notes_layout.setSpacing(10)
    notes_title = QLabel("Tips")
    notes_title.setObjectName("sectionTitle")
    notes_layout.addWidget(notes_title)

    for note in (
        "Use short triggers such as /addr or /promo.",
        "One rule can send text, an image, or both.",
        "Close always exits the app.",
    ):
        line = QLabel(note)
        line.setObjectName("listItem")
        line.setWordWrap(True)
        notes_layout.addWidget(line)
    notes_layout.addStretch(1)

    lower.addWidget(quick)
    lower.addWidget(notes)
    lower.setStretch(0, 3)
    lower.setStretch(1, 2)
    layout.addLayout(lower, 1)
    return page


def build_editor_page(window) -> QWidget:
    page = QWidget()
    page.setObjectName("pageRoot")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)

    header = create_card("heroCard")
    header_layout = QGridLayout(header)
    header_layout.setContentsMargins(22, 22, 22, 22)
    header_layout.setHorizontalSpacing(16)
    header_layout.setVerticalSpacing(8)

    title = QLabel("Word Editor")
    title.setObjectName("heroTitle")
    header_layout.addWidget(title, 0, 0)

    subtitle = QLabel(
        "Search, edit, and save rules in one workspace."
    )
    subtitle.setObjectName("muted")
    subtitle.setWordWrap(True)
    header_layout.addWidget(subtitle, 1, 0)

    search_wrap = QWidget()
    search_wrap.setObjectName("pageRoot")
    search_layout = QHBoxLayout(search_wrap)
    search_layout.setContentsMargins(0, 0, 0, 0)
    search_layout.setSpacing(8)

    window.search_edit = QLineEdit()
    window.search_edit.setPlaceholderText("Search trigger, output, image, or app")
    window.search_edit.textChanged.connect(window._refresh_rule_views)
    search_layout.addWidget(window.search_edit)

    window.filter_combo = QComboBox()
    window.filter_combo.addItems(
        [
            "all",
            "active",
            "inactive",
            "auto_enter_on",
            "auto_enter_off",
            "has_image",
            "text_only",
        ]
    )
    window.filter_combo.currentTextChanged.connect(window._refresh_rule_views)
    search_layout.addWidget(window.filter_combo)

    apply_button = QPushButton("Apply")
    apply_button.clicked.connect(window._refresh_rule_views)
    search_layout.addWidget(apply_button)
    header_layout.addWidget(search_wrap, 0, 1, 2, 1)
    layout.addWidget(header)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    splitter.setChildrenCollapsible(False)

    table_card = create_card()
    table_layout = QVBoxLayout(table_card)
    table_layout.setContentsMargins(16, 16, 16, 16)
    table_layout.setSpacing(10)

    table_header = QHBoxLayout()
    table_title = QLabel("Rules")
    table_title.setObjectName("sectionTitle")
    table_header.addWidget(table_title)
    table_header.addStretch(1)

    window.editor_summary = QLabel("")
    window.editor_summary.setObjectName("muted")
    table_header.addWidget(window.editor_summary)
    table_layout.addLayout(table_header)

    window.rule_table = QTableWidget(0, 4)
    window.rule_table.setObjectName("ruleTable")
    window.rule_table.setHorizontalHeaderLabels(["Trigger", "Status", "Enter", "Output"])
    window.rule_table.verticalHeader().setVisible(False)
    window.rule_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    window.rule_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    window.rule_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    window.rule_table.setAlternatingRowColors(True)
    window.rule_table.setShowGrid(False)
    window.rule_table.verticalHeader().setDefaultSectionSize(44)
    window.rule_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    window.rule_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
    window.rule_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
    window.rule_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
    window.rule_table.itemSelectionChanged.connect(window._update_rule_preview)
    table_layout.addWidget(window.rule_table, 1)
    splitter.addWidget(table_card)

    editor_scroll = QScrollArea()
    editor_scroll.setWidgetResizable(True)

    editor_content = QWidget()
    editor_content.setObjectName("pageRoot")
    editor_layout = QVBoxLayout(editor_content)
    editor_layout.setContentsMargins(0, 0, 0, 0)
    editor_layout.setSpacing(16)

    top_actions = create_card()
    top_layout = QVBoxLayout(top_actions)
    top_layout.setContentsMargins(16, 16, 16, 16)
    top_layout.setSpacing(8)

    panel_title = QLabel("Editor")
    panel_title.setObjectName("sectionTitle")
    top_layout.addWidget(panel_title)

    window.editor_mode_label = QLabel("Create a new rule")
    window.editor_mode_label.setObjectName("muted")
    top_layout.addWidget(window.editor_mode_label)

    new_rule_button = QPushButton("New Rule")
    new_rule_button.setObjectName("primaryButton")
    new_rule_button.clicked.connect(window._add)
    top_layout.addWidget(new_rule_button)

    action_row = QHBoxLayout()
    action_row.setSpacing(8)

    toggle_button = QPushButton("Toggle")
    toggle_button.clicked.connect(window._toggle)
    action_row.addWidget(toggle_button)

    delete_button = QPushButton("Delete")
    delete_button.setObjectName("dangerButton")
    delete_button.clicked.connect(window._delete)
    action_row.addWidget(delete_button)
    top_layout.addLayout(action_row)
    editor_layout.addWidget(top_actions)

    form = create_panel()
    form_layout = QVBoxLayout(form)
    form_layout.setContentsMargins(16, 16, 16, 16)
    form_layout.setSpacing(10)

    trigger_label = QLabel("Trigger")
    trigger_label.setObjectName("sectionTitle")
    form_layout.addWidget(trigger_label)

    window.rule_trigger_edit = QLineEdit()
    form_layout.addWidget(window.rule_trigger_edit)

    apps_label = QLabel("Target Apps (optional, comma-separated .exe names)")
    apps_label.setObjectName("fieldLabel")
    form_layout.addWidget(apps_label)

    window.rule_apps_edit = QLineEdit()
    window.rule_apps_edit.setPlaceholderText("discord.exe, chrome.exe")
    form_layout.addWidget(window.rule_apps_edit)

    output_label = QLabel("Output Text")
    output_label.setObjectName("fieldLabel")
    form_layout.addWidget(output_label)

    window.rule_output_edit = QPlainTextEdit()
    window.rule_output_edit.setMinimumHeight(180)
    form_layout.addWidget(window.rule_output_edit)

    image_label = QLabel("Image Path")
    image_label.setObjectName("fieldLabel")
    form_layout.addWidget(image_label)

    image_row = QHBoxLayout()
    image_row.setSpacing(8)
    window.rule_image_edit = QLineEdit()
    window.rule_image_edit.textChanged.connect(window._update_image_preview)
    image_row.addWidget(window.rule_image_edit, 1)

    browse_button = QPushButton("Browse")
    browse_button.clicked.connect(window._browse_rule_image)
    image_row.addWidget(browse_button)
    form_layout.addLayout(image_row)

    window.image_preview_label = QLabel("Image preview will appear here")
    window.image_preview_label.setObjectName("imagePreview")
    window.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.image_preview_label.setMinimumHeight(130)
    window.image_preview_label.setWordWrap(True)
    form_layout.addWidget(window.image_preview_label)

    window.rule_enabled_check = QCheckBox("Rule enabled")
    form_layout.addWidget(window.rule_enabled_check)

    window.rule_auto_enter_check = QCheckBox("Auto Enter for this rule")
    form_layout.addWidget(window.rule_auto_enter_check)

    save_row = QHBoxLayout()
    save_row.setSpacing(8)

    save_button = QPushButton("Save Rule")
    save_button.setObjectName("primaryButton")
    save_button.clicked.connect(window._save_editor_rule)
    save_row.addWidget(save_button)

    reset_button = QPushButton("Reset Form")
    reset_button.clicked.connect(window._clear_editor_form)
    save_row.addWidget(reset_button)
    form_layout.addLayout(save_row)
    editor_layout.addWidget(form)

    preview = create_panel()
    preview_layout = QVBoxLayout(preview)
    preview_layout.setContentsMargins(16, 16, 16, 16)
    preview_layout.setSpacing(10)

    preview_title = QLabel("Selected Rule")
    preview_title.setObjectName("sectionTitle")
    preview_layout.addWidget(preview_title)

    window.rule_preview = QPlainTextEdit()
    window.rule_preview.setObjectName("previewBox")
    window.rule_preview.setReadOnly(True)
    window.rule_preview.setMinimumHeight(220)
    preview_layout.addWidget(window.rule_preview)
    editor_layout.addWidget(preview)
    editor_layout.addStretch(1)

    editor_scroll.setWidget(editor_content)
    splitter.addWidget(editor_scroll)
    splitter.setSizes([760, 460])
    layout.addWidget(splitter, 1)
    return page


def build_log_page(window) -> QWidget:
    page = QWidget()
    page.setObjectName("pageRoot")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)

    hero = create_card("heroCard")
    hero_layout = QGridLayout(hero)
    hero_layout.setContentsMargins(22, 22, 22, 22)
    hero_layout.setHorizontalSpacing(16)
    hero_layout.setVerticalSpacing(8)

    title = QLabel("Log")
    title.setObjectName("heroTitle")
    hero_layout.addWidget(title, 0, 0)

    subtitle = QLabel("Runtime activity for matches, injections, and backups.")
    subtitle.setObjectName("muted")
    subtitle.setWordWrap(True)
    hero_layout.addWidget(subtitle, 1, 0)

    log_actions = QHBoxLayout()
    log_actions.setSpacing(8)

    copy_button = QPushButton("Copy Log")
    copy_button.clicked.connect(window._copy_log)
    log_actions.addWidget(copy_button)

    clear_button = QPushButton("Clear Log")
    clear_button.clicked.connect(window._clear_log)
    log_actions.addWidget(clear_button)

    hero_layout.addLayout(
        log_actions,
        0,
        1,
        2,
        1,
        alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
    )
    layout.addWidget(hero)

    log_card = create_card()
    log_layout = QVBoxLayout(log_card)
    log_layout.setContentsMargins(18, 18, 18, 18)
    window.log_text = QPlainTextEdit()
    window.log_text.setObjectName("previewBox")
    window.log_text.setPlaceholderText("Runtime activity will appear here.")
    window.log_text.setReadOnly(True)
    log_layout.addWidget(window.log_text)
    layout.addWidget(log_card, 1)
    return page


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

    subtitle = QLabel(
        "Manage app behavior, tray options, startup mode, and backups."
    )
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


def build_license_page(window) -> QWidget:
    page = QWidget()
    page.setObjectName("pageRoot")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)

    hero = create_card("heroCard")
    hero_layout = QVBoxLayout(hero)
    hero_layout.setContentsMargins(22, 22, 22, 22)
    hero_layout.setSpacing(6)

    title = QLabel("License")
    title.setObjectName("heroTitle")
    hero_layout.addWidget(title)

    subtitle = QLabel("Usage terms and ownership details for FastWord.")
    subtitle.setObjectName("muted")
    subtitle.setWordWrap(True)
    hero_layout.addWidget(subtitle)
    layout.addWidget(hero)

    card = create_card()
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(20, 20, 20, 20)
    card_layout.setSpacing(10)

    card_title = QLabel("FastWord Proprietary License")
    card_title.setObjectName("sectionTitle")
    card_layout.addWidget(card_title)

    card_note = QLabel("This build is distributed as proprietary software.")
    card_note.setObjectName("muted")
    card_note.setWordWrap(True)
    card_layout.addWidget(card_note)

    developer_name = QLabel(f"Developer: {window.developer_name}")
    developer_name.setObjectName("fieldLabel")
    card_layout.addWidget(developer_name)

    github_label = QLabel(f"GitHub: {window.github_username} - {window.github_url}")
    github_label.setObjectName("muted")
    github_label.setWordWrap(True)
    card_layout.addWidget(github_label)

    window.license_text_box = QPlainTextEdit()
    window.license_text_box.setObjectName("previewBox")
    window.license_text_box.setReadOnly(True)
    window.license_text_box.setMinimumHeight(420)
    window.license_text_box.setPlainText(window.license_text_value)
    card_layout.addWidget(window.license_text_box)

    action_row = QHBoxLayout()
    action_row.setSpacing(8)

    copy_button = QPushButton("Copy License")
    copy_button.clicked.connect(window._copy_license_text)
    action_row.addWidget(copy_button)

    github_button = QPushButton("Open GitHub")
    github_button.clicked.connect(window._open_github_link)
    action_row.addWidget(github_button)

    donate_button = QPushButton("Open Donate Page")
    donate_button.setObjectName("primaryButton")
    donate_button.clicked.connect(lambda: window._show_page("donate"))
    action_row.addWidget(donate_button)
    action_row.addStretch(1)
    card_layout.addLayout(action_row)

    layout.addWidget(card, 1)
    return page


def build_donate_page(window) -> QWidget:
    page = QWidget()
    page.setObjectName("pageRoot")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)

    hero = create_card("heroCard")
    hero_layout = QVBoxLayout(hero)
    hero_layout.setContentsMargins(22, 22, 22, 22)
    hero_layout.setSpacing(6)

    title = QLabel("Donate")
    title.setObjectName("heroTitle")
    hero_layout.addWidget(title)

    subtitle = QLabel("Support FastWord development through PayPal or direct bank transfer.")
    subtitle.setObjectName("muted")
    subtitle.setWordWrap(True)
    hero_layout.addWidget(subtitle)

    layout.addWidget(hero)

    methods = QHBoxLayout()
    methods.setSpacing(12)

    paypal_card = create_card()
    paypal_layout = QVBoxLayout(paypal_card)
    paypal_layout.setContentsMargins(20, 20, 20, 20)
    paypal_layout.setSpacing(10)

    paypal_title = QLabel("PayPal")
    paypal_title.setObjectName("sectionTitle")
    paypal_layout.addWidget(paypal_title)

    paypal_note = QLabel(window.paypal_url)
    paypal_note.setObjectName("fieldLabel")
    paypal_note.setWordWrap(True)
    paypal_layout.addWidget(paypal_note)

    paypal_row = QHBoxLayout()
    paypal_row.setSpacing(8)

    open_paypal_button = QPushButton("Open PayPal")
    open_paypal_button.setObjectName("primaryButton")
    open_paypal_button.clicked.connect(window._open_paypal_link)
    open_paypal_button.setEnabled(bool(window.paypal_url))
    paypal_row.addWidget(open_paypal_button)

    copy_paypal_button = QPushButton("Copy PayPal Link")
    copy_paypal_button.clicked.connect(window._copy_paypal_link)
    copy_paypal_button.setEnabled(bool(window.paypal_url))
    paypal_row.addWidget(copy_paypal_button)
    paypal_row.addStretch(1)
    paypal_layout.addLayout(paypal_row)

    paypal_hint = QLabel(f"Developer: {window.developer_name} | GitHub: {window.github_username}")
    paypal_hint.setObjectName("listItem")
    paypal_hint.setWordWrap(True)
    paypal_layout.addWidget(paypal_hint)
    paypal_layout.addStretch(1)

    bank_card = create_card()
    bank_layout = QVBoxLayout(bank_card)
    bank_layout.setContentsMargins(20, 20, 20, 20)
    bank_layout.setSpacing(10)

    bank_title = QLabel("Bank Transfer")
    bank_title.setObjectName("sectionTitle")
    bank_layout.addWidget(bank_title)

    bank_line_1 = QLabel(f"Bank: {window.bank_name}")
    bank_line_1.setObjectName("fieldLabel")
    bank_layout.addWidget(bank_line_1)

    bank_line_2 = QLabel(f"Account Number: {window.bank_account_number}")
    bank_line_2.setObjectName("fieldLabel")
    bank_layout.addWidget(bank_line_2)

    bank_line_3 = QLabel(f"Account Name: {window.bank_account_name}")
    bank_line_3.setObjectName("fieldLabel")
    bank_layout.addWidget(bank_line_3)

    copy_number_button = QPushButton("Copy Account Number")
    copy_number_button.setObjectName("primaryButton")
    copy_number_button.clicked.connect(window._copy_bank_account_number)
    bank_layout.addWidget(copy_number_button)

    copy_name_button = QPushButton("Copy Account Name")
    copy_name_button.clicked.connect(window._copy_bank_account_name)
    bank_layout.addWidget(copy_name_button)

    bank_note = QLabel("Thank you for supporting the project.")
    bank_note.setObjectName("listItem")
    bank_note.setWordWrap(True)
    bank_layout.addWidget(bank_note)
    bank_layout.addStretch(1)

    methods.addWidget(paypal_card)
    methods.addWidget(bank_card)
    layout.addLayout(methods, 1)
    return page
