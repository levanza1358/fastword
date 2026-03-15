APP_STYLESHEET = """
QWidget {
    color: #ecf3ff;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QLabel {
    background: transparent;
}
QMainWindow, QWidget#appRoot {
    background: #0c1320;
}
QWidget#contentRoot, QWidget#pageRoot {
    background: transparent;
}
QFrame#sidebar {
    background: #0f1726;
    border-right: 1px solid #1a273d;
}
QFrame#sidebarBrand {
    background: transparent;
    border: none;
}
QFrame#navGroup, QFrame#storageCard {
    background: transparent;
    border: none;
}
QFrame#heroCard {
    background: #121b2b;
    border: 1px solid #1b2940;
    border-radius: 12px;
}
QFrame#card {
    background: #101a2a;
    border: 1px solid #1b2940;
    border-radius: 12px;
}
QFrame#panel {
    background: #101a2a;
    border: 1px solid #1b2940;
    border-radius: 12px;
}
QFrame#statCard {
    background: #101a2a;
    border: 1px solid #1b2940;
    border-radius: 12px;
}
QLabel#heroTitle {
    font-size: 18pt;
    font-weight: 700;
}
QLabel#sectionTitle {
    font-size: 11pt;
    font-weight: 600;
}
QLabel#muted {
    color: #96a6c0;
}
QLabel#sidebarTitle {
    font-size: 18px;
    font-weight: 700;
}
QLabel#sidebarKicker {
    color: #7f91ad;
    font-size: 8.5pt;
    font-weight: 600;
}
QLabel#sidebarBadge {
    background: #101a2a;
    border: 1px solid #24344d;
    border-radius: 10px;
    padding: 6px 12px;
    font-weight: 600;
}
QLabel#brandMark {
    background: #4f8cff;
    color: white;
    border-radius: 11px;
    font-size: 15px;
    font-weight: 800;
}
QLabel#brandIcon {
    background: transparent;
    border: none;
    padding: 0;
}
QLabel#statLabel {
    color: #8ea2c2;
    font-size: 8.5pt;
    font-weight: 600;
}
QLabel#statValue {
    font-size: 18pt;
    font-weight: 700;
}
QLabel#metricNote {
    color: #8c9bb6;
}
QLabel#listItem {
    color: #a4b4cd;
    padding: 4px 0;
}
QLabel#fieldLabel {
    color: #9fb0c9;
    font-size: 9.5pt;
    font-weight: 600;
}
QLabel#pathText {
    color: #8fa1bd;
    font-size: 8.8pt;
}
QPushButton {
    background: #132036;
    border: 1px solid #263955;
    border-radius: 9px;
    padding: 8px 14px;
    min-height: 18px;
    font-weight: 600;
}
QPushButton:hover {
    background: #18263d;
    border-color: #365078;
}
QPushButton#primaryButton {
    background: #4f86f0;
    color: white;
    border: 1px solid #5e92f6;
}
QPushButton#primaryButton:hover {
    background: #467ce8;
    border-color: #6e9ff7;
}
QPushButton#dangerButton {
    background: #6f2b36;
    color: white;
    border: 1px solid #8a404c;
}
QPushButton#dangerButton:hover {
    background: #7d3140;
}
QPushButton#navButton {
    text-align: left;
    background: transparent;
    border: 1px solid transparent;
    padding: 9px 12px;
    border-radius: 10px;
    font-size: 10pt;
}
QPushButton#navButton:hover {
    background: #142033;
    border-color: #24344d;
}
QPushButton#navButton[active="true"] {
    background: #16253d;
    color: #b7cff8;
    border-color: #304b70;
}
QLineEdit, QTextEdit, QComboBox, QTableWidget, QPlainTextEdit, QSpinBox {
    background: #0c1523;
    border: 1px solid #21324c;
    border-radius: 9px;
    padding: 8px;
    selection-background-color: #244879;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QSpinBox:focus {
    border: 1px solid #5c91e9;
    background: #0c1625;
}
QComboBox QAbstractItemView {
    background: #0f192c;
    border: 1px solid #27405f;
    selection-background-color: #1f3f69;
    color: #ecf3ff;
}
QTableWidget {
    background: #0d1727;
    border-radius: 9px;
    gridline-color: #1a2b43;
    alternate-background-color: #0e1728;
}
QTableWidget#ruleTable {
    border: 1px solid #233754;
}
QHeaderView::section {
    background: #14233b;
    color: #dbe8ff;
    border: none;
    padding: 10px;
    font-weight: 700;
}
QTableWidget::item:selected {
    background: #17345b;
}
QPlainTextEdit#previewBox {
    background: #0c1525;
    border: 1px solid #21344f;
    border-radius: 9px;
    font-family: "Consolas";
}
QLabel#imagePreview {
    background: #0c1525;
    border: 1px solid #21344f;
    border-radius: 9px;
    padding: 10px;
    color: #8ea4c6;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a456b;
    min-height: 30px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QCheckBox {
    spacing: 8px;
    color: #e4eeff;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
}
QCheckBox::indicator:unchecked {
    border: 1px solid #4d6488;
    background: #08111d;
}
QCheckBox::indicator:checked {
    border: 1px solid #5f97f3;
    background: #4f8cff;
}
"""

STATUS_RUNNING = "background:#163626;color:#9be6ba;border:1px solid #2f5c42;border-radius:10px;padding:7px 12px;font-weight:700;"
STATUS_STOPPED = "background:#3a1f27;color:#ffc0c4;border:1px solid #6f3945;border-radius:10px;padding:7px 12px;font-weight:700;"
