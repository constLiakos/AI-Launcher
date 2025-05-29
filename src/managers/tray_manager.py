# Add missing imports at the top
import logging
from PyQt5.QtWidgets import (QWidget, QAction, QSystemTrayIcon, QMenu, QAction, QSystemTrayIcon)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QFont, QIcon

from utils.constants import Style, Colors, Text, Timing, TrayIcon

class TrayManager(QSystemTrayIcon):
    def __init__(self, parent, logger: logging.Logger, show_window, hide_window, open_settings, quit_application, tray_icon_activated):
        super().__init__()
        self.parent = parent
        self.show_window = show_window
        self.hide_window = hide_window
        self.open_settings = open_settings
        self.quit_application = quit_application
        self.tray_icon_activated =tray_icon_activated

    def setup_system_tray(self):
        """Setup system tray icon and menu."""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available on this system")
            return

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Set icon (you can use a custom icon file or create one)
        # For now, using a simple colored icon
        icon = self.create_tray_icon()
        self.tray_icon.setIcon(icon)

        # Create context menu
        tray_menu = QMenu()

        # Show/Hide action
        show_action = QAction(Text.TRAY_SHOW, self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        hide_action = QAction(Text.TRAY_HIDE, self)
        hide_action.triggered.connect(self.hide_window)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)

        tray_menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        # Set menu to tray icon
        self.tray_icon.setContextMenu(tray_menu)

        # Connect double-click to show window
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # Show tray icon
        self.tray_icon.show()

        # Set tooltip
        self.tray_icon.setToolTip(Text.TRAY_TOOLTIP)


    def create_tray_icon(self):
        """Create a simple tray icon."""
        # Create a simple icon (you can replace this with a custom icon file)
        pixmap = QPixmap(TrayIcon.SIZE, TrayIcon.SIZE)
        pixmap.fill(Colors.PRIMARY_BLUE)  # Blue color

        # Draw AI text on it
        painter = QPainter(pixmap)
        painter.setPen(Colors.WHITE)
        painter.setFont(QFont(TrayIcon.FONT_FAMILY,
                        Style.TRAY_ICON_FONT_SIZE, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, Text.TRAY_ICON_TEXT)
        painter.end()

        return QIcon(pixmap)
