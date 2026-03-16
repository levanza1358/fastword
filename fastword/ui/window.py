from __future__ import annotations

import ctypes
import os
import sys
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from ..app_info import (
    APP_DESKTOP_ID,
    APP_LICENSE_TEXT,
    APP_MARK,
    APP_NAME,
    APP_VERSION,
    DEVELOPER_NAME,
    GITHUB_URL,
    GITHUB_USERNAME,
    PAYPAL_DISPLAY_TEXT,
    PAYPAL_URL,
)
from ..engine import FastWordEngine
from ..qt_theme import APP_STYLESHEET
from ..runtime import resource_path
from ..startup import is_enabled as is_startup_enabled
from ..storage import load_config, load_rules
from .pages import (
    build_donate_page,
    build_editor_page,
    build_home_page,
    build_license_page,
    build_log_page,
    build_settings_page,
)
from .window_actions import WindowActionsMixin
from .window_rules import WindowRulesMixin
from .window_settings import WindowSettingsMixin


class LogBridge(QObject):
    message = pyqtSignal(str)


class FastWordWindow(WindowActionsMixin, WindowRulesMixin, WindowSettingsMixin, QMainWindow):
    def __init__(self):
        self._quitting = False
        self._hidden_to_tray = False
        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._preview_pixmap: Optional[QPixmap] = None
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1260, 820)
        self.setMinimumSize(1080, 700)

        self.engine = FastWordEngine()
        self.log_bridge = LogBridge()
        self.log_bridge.message.connect(self._append_log)
        self.engine.log_callback = self.log_bridge.message.emit

        self.rules = load_rules()
        self.settings = load_config()
        self.settings["start_with_windows"] = is_startup_enabled()

        self.filtered_rule_indices: list[int] = []
        self.nav_buttons: dict[str, QPushButton] = {}
        self.page_index: dict[str, int] = {}
        self.editor_mode = "add"
        self.editor_rule_index: Optional[int] = None
        self.log_lines: list[str] = []
        self.license_text_value = APP_LICENSE_TEXT
        self.developer_name = DEVELOPER_NAME
        self.github_username = GITHUB_USERNAME
        self.github_url = GITHUB_URL
        self.paypal_url = PAYPAL_URL
        self.paypal_display_text = PAYPAL_DISPLAY_TEXT

        self.engine.set_rules(self.rules)
        self.engine.configure(
            auto_enter=self.settings.get("auto_enter", True),
            global_delay_ms=self.settings.get("global_delay_ms", 120),
        )

        self._apply_window_icon()
        self._build_shell()
        self._load_settings_into_form()
        self._refresh_rule_views()
        self._update_status()
        self._show_page("home")
        self._sync_tray_icon()
        QTimer.singleShot(0, self._auto_start_engine_if_needed)

    def _apply_window_icon(self) -> None:
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_DESKTOP_ID)
        except Exception:
            pass

        icon = QIcon()
        for candidate in (
            resource_path("assets", "app.ico"),
            resource_path("assets", "app.png"),
        ):
            if os.path.exists(candidate):
                icon = QIcon(candidate)
                if not icon.isNull():
                    break

        if not icon.isNull():
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)

    def _build_shell(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 18, 18, 18)
        sidebar_layout.setSpacing(16)

        brand_card = QFrame()
        brand_card.setObjectName("sidebarBrand")
        brand_layout = QVBoxLayout(brand_card)
        brand_layout.setContentsMargins(10, 6, 10, 6)
        brand_layout.setSpacing(10)

        brand = QLabel()
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFixedSize(48, 48)
        brand.setObjectName("brandIcon")
        brand_pixmap = QPixmap(resource_path("assets", "app.png"))
        if not brand_pixmap.isNull():
            brand.setPixmap(
                brand_pixmap.scaled(
                    48,
                    48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            brand.setText(APP_MARK)
            brand.setObjectName("brandMark")
        brand_layout.addWidget(brand, alignment=Qt.AlignmentFlag.AlignLeft)

        sidebar_title = QLabel(APP_NAME)
        sidebar_title.setObjectName("sidebarTitle")
        brand_layout.addWidget(sidebar_title)

        sidebar_subtitle = QLabel("Desktop text expander.")
        sidebar_subtitle.setObjectName("muted")
        sidebar_subtitle.setWordWrap(True)
        brand_layout.addWidget(sidebar_subtitle)

        self.sidebar_status_badge = QLabel("Engine Stopped")
        self.sidebar_status_badge.setObjectName("sidebarBadge")
        brand_layout.addWidget(self.sidebar_status_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        sidebar_layout.addWidget(brand_card)

        nav_group = QFrame()
        nav_group.setObjectName("navGroup")
        nav_layout = QVBoxLayout(nav_group)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(6)

        for key, label in (
            ("home", "Home"),
            ("editor", "Word Editor"),
            ("log", "Activity Log"),
            ("settings", "Settings"),
            ("license", "License"),
            ("donate", "Donate"),
        ):
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.clicked.connect(lambda _checked=False, page=key: self._show_page(page))
            nav_layout.addWidget(button)
            self.nav_buttons[key] = button

        sidebar_layout.addWidget(nav_group)
        sidebar_layout.addStretch(1)

        content = QWidget()
        content.setObjectName("contentRoot")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(0)

        self.pages = QStackedWidget()
        self.pages.addWidget(build_home_page(self))
        self.page_index["home"] = 0
        self.pages.addWidget(build_editor_page(self))
        self.page_index["editor"] = 1
        self.pages.addWidget(build_log_page(self))
        self.page_index["log"] = 2
        self.pages.addWidget(build_settings_page(self))
        self.page_index["settings"] = 3
        self.pages.addWidget(build_license_page(self))
        self.page_index["license"] = 4
        self.pages.addWidget(build_donate_page(self))
        self.page_index["donate"] = 5
        content_layout.addWidget(self.pages)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(content, 1)
        self.setCentralWidget(root)

    def _show_page(self, page_name: str) -> None:
        if page_name not in self.page_index:
            return
        if page_name == "settings":
            self._load_settings_into_form()
        self.pages.setCurrentIndex(self.page_index[page_name])
        for key, button in self.nav_buttons.items():
            button.setProperty("active", key == page_name)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()


class FastWordGUI:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        self.app.setQuitOnLastWindowClosed(True)
        self.app.setStyleSheet(APP_STYLESHEET)
        self.window = FastWordWindow()

    def run(self):
        self.window.show()
        return self.app.exec()
