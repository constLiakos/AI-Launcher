from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QTextBrowser)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from managers.style_manager import StyleManager
from utils.constants import AboutDialogSize, SettingsDialogSize, Text
from PyQt5.QtGui import QFont, QFontDatabase

from utils.version import VERSION

class AboutDialog(QDialog):
    def __init__(self, logger, parent=None):
        super().__init__(parent)
        self.logger = logger.getChild('about_dialog')
        self.style_manager = StyleManager(logger)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.logger.debug("Setting up AboutDialog UI")
        self.setWindowTitle("About")
        self.setFixedSize(AboutDialogSize.WINDOW_WIDTH, AboutDialogSize.WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(AboutDialogSize.MAIN_LAYOUT_MARGIN, AboutDialogSize.MAIN_LAYOUT_MARGIN, AboutDialogSize.MAIN_LAYOUT_MARGIN, AboutDialogSize.MAIN_LAYOUT_MARGIN)
        layout.setSpacing(AboutDialogSize.MAIN_LAYOUT_SPACING)
        
        # Title
        title_label = QLabel("About This Project")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel(f"Version {VERSION}")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Project info
        info_text = QTextBrowser()
        info_text.setObjectName("aboutTextEdit")
        info_text.setAcceptRichText(True)

        info_text.setOpenExternalLinks(True)
        self.setup_emoji_font(info_text)

        info_text.setHtml(Text.ABOUT_DIALOGUE_TEXT)
        layout.addWidget(info_text)
        
        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("saveButton")
        close_btn.setMinimumHeight(35)
        close_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def apply_styles(self):
        """Apply styles using StyleManager."""
        self.logger.debug("Applying styles to AboutDialog")
        self.setStyleSheet(self.style_manager.get_settings_dialog_styles())

    def setup_emoji_font(self, widget):
        """Configure font for better emoji support."""
        font = QFont()
        
        # Try different fonts that support color emojis
        emoji_fonts = [
            "Segoe UI Emoji",      # Windows
            "Apple Color Emoji",   # macOS
            "Noto Color Emoji",    # Linux
            "Twemoji",             # Web fallback
            "Segoe UI",            # Windows fallback
            "Arial",               # Universal fallback
        ]
        
        font_db = QFontDatabase()
        for font_name in emoji_fonts:
            font.setFamily(font_name)
            # Use families() method to check if font exists
            if font_name in font_db.families():
                self.logger.debug(f"Using font: {font_name}")
                break
        
        font.setPointSize(12)
        widget.setFont(font)