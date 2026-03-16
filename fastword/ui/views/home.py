from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..components import create_card, create_stat_card


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
