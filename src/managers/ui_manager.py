import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QTextBrowser, QFrame, QShortcut,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QFontDatabase
from utils.constants import (ElementSize, Files, Text, WindowSize)


class UIManager:
    def __init__(self, parent_window, logger, config, style_manager):
        self.parent = parent_window
        self.logger = logger
        self.config = config
        self.style_manager = style_manager

        # UI Components (will be created in setup_ui)
        self.main_container = None
        self.input_field = None
        self.response_area = None
        self.stt_button = None
        self.settings_button = None
        self.copy_button = None

    def setup_ui(self):
        """Create and setup all UI components."""
        self._setup_window_properties()
        self._create_main_container()
        self._create_input_section()
        self._create_response_section()
        self._create_copy_button()
        self._setup_shortcuts()

    def _setup_window_properties(self):
        """Configure window properties."""
        self.parent.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.parent.setAttribute(Qt.WA_TranslucentBackground)
        self.parent.resize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)
        self.parent.setMinimumSize(
            WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)

    def _create_main_container(self):
        """Create the main container widget."""
        central_widget = QWidget()
        self.parent.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")
        main_layout.addWidget(self.main_container)

    def _create_input_section(self):
        """Create input field and buttons."""
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(
            ElementSize.CONTAINER_MARGIN_HORIZONTAL,
            ElementSize.CONTAINER_MARGIN_VERTICAL,
            ElementSize.CONTAINER_MARGIN_HORIZONTAL,
            ElementSize.CONTAINER_MARGIN_VERTICAL
        )

        input_layout = QHBoxLayout()
        input_layout.setSpacing(ElementSize.CONTAINER_SPACING)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("inputField")
        self.input_field.setPlaceholderText(Text.INPUT_PLACEHOLDER)
        input_layout.addWidget(self.input_field)

        # STT button
        self.stt_button = QPushButton()
        self.stt_button.setObjectName("sttButton")
        self.stt_button.setIcon(QIcon(str(Files.MIC_IDLE_ICON_PATH)))
        self.stt_button.setFixedSize(
            ElementSize.SETTINGS_BUTTON_SIZE, ElementSize.SETTINGS_BUTTON_SIZE)
        input_layout.addWidget(self.stt_button)

        # Settings button
        self.settings_button = QPushButton()
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setIcon(QIcon(str(Files.SETTINGS_GEAR_ICON_PATH)))
        self.settings_button.setFixedSize(
            ElementSize.SETTINGS_BUTTON_SIZE, ElementSize.SETTINGS_BUTTON_SIZE)
        input_layout.addWidget(self.settings_button)

        container_layout.addLayout(input_layout)

    def _create_response_section(self):
        """Create response area."""
        container_layout = self.main_container.layout()

        self.response_area = QTextBrowser()
        self.response_area.setObjectName("responseArea")
        self.response_area.setAcceptRichText(True)
        self.response_area.setOpenExternalLinks(True)
        self.response_area.setVisible(False)
        self.response_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setup_emoji_font(self.response_area)
        container_layout.addWidget(self.response_area)
        container_layout.setStretchFactor(
            container_layout.itemAt(0).layout(), 0)  # Input section
        # Response area takes remaining space
        container_layout.setStretchFactor(self.response_area, 1)
        container_layout.addStretch()

    def _create_copy_button(self):
        """Create copy button."""
        self.copy_button = QPushButton(Text.COPY_BUTTON)
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setFixedSize(
            ElementSize.COPY_BUTTON_WIDTH, ElementSize.COPY_BUTTON_HEIGHT)
        self.copy_button.setVisible(False)
        self.copy_button.setParent(self.main_container)
        self.copy_button.raise_()

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # ESC to hide to tray
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self.parent)
        escape_shortcut.activated.connect(self.parent.hide_window)

        # Ctrl+Q to quit completely
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self.parent)
        quit_shortcut.activated.connect(self.parent.quit_application)

    def connect_signals(self, callbacks):
        """Connect UI signals to callbacks."""
        if 'input_changed' in callbacks:
            self.input_field.textChanged.connect(callbacks['input_changed'])
        if 'return_pressed' in callbacks:
            self.input_field.returnPressed.connect(callbacks['return_pressed'])
        if 'stt_clicked' in callbacks:
            self.stt_button.clicked.connect(callbacks['stt_clicked'])
        if 'settings_clicked' in callbacks:
            self.settings_button.clicked.connect(callbacks['settings_clicked'])
        if 'copy_clicked' in callbacks:
            self.copy_button.clicked.connect(callbacks['copy_clicked'])

    def update_stt_button_visibility(self, enabled):
        """Update STT button visibility."""
        self.stt_button.setVisible(enabled)
        self.stt_button.setEnabled(enabled)

    def update_stt_button_appearance(self, state):
        """Update STT button appearance."""
        if state == "recording":
            self.stt_button.setIcon(QIcon(str(Files.MIC_RECORDING_ICON_PATH)))
        else:
            self.stt_button.setIcon(QIcon(str(Files.MIC_IDLE_ICON_PATH)))

        self.stt_button.style().unpolish(self.stt_button)
        self.stt_button.style().polish(self.stt_button)

    def set_input_state(self, state):
        """Set visual state of input field."""
        if state == "thinking":
            self.input_field.setObjectName("inputFieldThinking")
        elif state == "typing":
            self.input_field.setObjectName("inputFieldTyping")
        else:
            self.input_field.setObjectName("inputField")

        self.input_field.setStyle(self.input_field.style())

    def position_copy_button(self):
        """Position copy button in response area."""
        if self.response_area.isVisible():
            response_pos = self.response_area.pos()
            response_geometry = self.response_area.geometry()

            button_x = (response_pos.x() + response_geometry.width() -
                        self.copy_button.width() - ElementSize.SCROLLBAR_SIZE -
                        ElementSize.COPY_BUTTON_RIGHT_MARGIN)
            button_y = response_pos.y() + ElementSize.COPY_BUTTON_RIGHT_MARGIN

            self.copy_button.move(button_x, button_y)
            self.copy_button.raise_()
            self.copy_button.setVisible(True)

    def show_response_area(self):
        """Show response area and copy button."""
        self.response_area.setVisible(True)
        self.copy_button.setVisible(True)
        self.position_copy_button()

    def hide_response_area(self):
        """Hide response area and copy button."""
        self.response_area.setVisible(False)
        self.copy_button.setVisible(False)

    def setup_emoji_font(self, widget):
        """Configure font for emoji support."""
        font = QFont()
        emoji_fonts = ["Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji",
                       "Twemoji", "Segoe UI", "Arial"]

        font_db = QFontDatabase()
        for font_name in emoji_fonts:
            font.setFamily(font_name)
            if font_name in font_db.families():
                self.logger.debug(f"Using font: {font_name}")
                break

        font.setPointSize(12)
        widget.setFont(font)
