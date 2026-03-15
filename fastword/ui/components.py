from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout


def create_card(object_name: str = "card") -> QFrame:
    card = QFrame()
    card.setObjectName(object_name)
    return card


def create_panel(object_name: str = "panel") -> QFrame:
    panel = QFrame()
    panel.setObjectName(object_name)
    return panel


def create_stat_card(title: str, note: str) -> tuple[QFrame, QLabel]:
    card = create_card("statCard")
    card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(6)

    title_label = QLabel(title)
    title_label.setObjectName("statLabel")
    layout.addWidget(title_label)

    value_label = QLabel("0")
    value_label.setObjectName("statValue")
    layout.addWidget(value_label)

    note_label = QLabel(note)
    note_label.setObjectName("metricNote")
    note_label.setWordWrap(True)
    layout.addWidget(note_label)
    return card, value_label
