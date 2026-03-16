from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QPlainTextEdit, QLabel, QPushButton, QVBoxLayout, QWidget

from ..components import create_card


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
