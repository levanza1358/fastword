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
    QSplitter,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from ..components import create_card, create_panel


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

    subtitle = QLabel("Search, edit, and save rules in one workspace.")
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
