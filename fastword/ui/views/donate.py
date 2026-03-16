from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..components import create_card


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

    subtitle = QLabel("Support FastWord development through PayPal.")
    subtitle.setObjectName("muted")
    subtitle.setWordWrap(True)
    hero_layout.addWidget(subtitle)
    layout.addWidget(hero)

    donate_card = create_card()
    donate_layout = QVBoxLayout(donate_card)
    donate_layout.setContentsMargins(28, 28, 28, 28)
    donate_layout.setSpacing(14)

    donate_title = QLabel("Support Link")
    donate_title.setObjectName("sectionTitle")
    donate_layout.addWidget(donate_title)

    donate_note = QLabel("If FastWord saves you time, you can support future updates through PayPal.")
    donate_note.setObjectName("muted")
    donate_note.setWordWrap(True)
    donate_layout.addWidget(donate_note)

    paypal_link = QLabel(window.paypal_url)
    paypal_link.setObjectName("fieldLabel")
    paypal_link.setWordWrap(True)
    donate_layout.addWidget(paypal_link)

    action_row = QHBoxLayout()
    action_row.setSpacing(8)

    open_paypal_button = QPushButton("Open PayPal")
    open_paypal_button.setObjectName("primaryButton")
    open_paypal_button.clicked.connect(window._open_paypal_link)
    open_paypal_button.setEnabled(bool(window.paypal_url))
    action_row.addWidget(open_paypal_button)

    copy_paypal_button = QPushButton("Copy PayPal Link")
    copy_paypal_button.clicked.connect(window._copy_paypal_link)
    copy_paypal_button.setEnabled(bool(window.paypal_url))
    action_row.addWidget(copy_paypal_button)

    github_button = QPushButton("Open GitHub")
    github_button.clicked.connect(window._open_github_link)
    action_row.addWidget(github_button)
    action_row.addStretch(1)
    donate_layout.addLayout(action_row)

    footer = QLabel(f"Developer: {window.developer_name} | GitHub: {window.github_username}")
    footer.setObjectName("listItem")
    footer.setWordWrap(True)
    donate_layout.addWidget(footer)
    donate_layout.addStretch(1)

    layout.addWidget(donate_card, 1)
    return page
