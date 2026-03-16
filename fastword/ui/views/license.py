from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from ..components import create_card


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
