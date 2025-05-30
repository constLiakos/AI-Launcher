import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
                             QPushButton, QTextBrowser, QFrame, QShortcut,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QFontDatabase
from utils.constants import (ElementSize, Files, InputSettings, Text, WindowSize)


class UIManager:
    def __init__(self, parent_window, logger, config):
        self.parent = parent_window
        self.logger = logger.getChild('ui_manager')
        self.config = config

        self.main_container = None
        self.input_field = None
        self.response_area = None
        self.stt_button = None
        self.settings_button = None
        self.copy_button = None
        self.multiline_input = False
        self.multiline_toggle_button = None

        self.original_input_height = None
        self.original_window_height = None
        self.min_window_height = WindowSize.COMPACT_HEIGHT
        self.animation_callbacks = {}
        self.state_manager_callbacks = {}

        self.multiline_toggle_debounce_timer = QTimer()
        self.multiline_toggle_debounce_timer.setSingleShot(True)
        self.multiline_toggle_debounce_timer.timeout.connect(self._handle_multiline_toggle_debounced)
        self.pending_multiline_callback = None

    def setup_ui(self, multiline_input=False):
        """Create and setup all UI components."""
        self.multiline_input = multiline_input
        self._setup_window_properties()
        self._create_main_container()
        self._create_input_section()
        self._create_response_section()
        self._create_copy_button()
        self._setup_shortcuts()

    def connect_signals(self, callbacks):
        """Connect UI signals to callbacks."""
        if 'input_changed' in callbacks:
            if hasattr(self.input_field, 'toPlainText'):
                # QTextEdit - textChanged doesn't pass text
                self.input_field.textChanged.connect(lambda: callbacks['input_changed'](self.get_input_text()))
            else:
                # QLineEdit - textChanged passes text
                self.input_field.textChanged.connect(callbacks['input_changed'])
        
        if 'return_pressed' in callbacks:
            # Install event filter on parent to handle key events
            self.input_field.installEventFilter(self.parent)
        
        if 'stt_clicked' in callbacks:
            self.stt_button.clicked.connect(callbacks['stt_clicked'])
        if 'settings_clicked' in callbacks:
            self.settings_button.clicked.connect(callbacks['settings_clicked'])
        if 'copy_clicked' in callbacks:
            self.copy_button.clicked.connect(callbacks['copy_clicked'])
        # Store animation callbacks
        if 'start_thinking_animation' in callbacks:
            self.animation_callbacks['start_thinking'] = callbacks['start_thinking_animation']
        if 'stop_thinking_animation' in callbacks:
            self.animation_callbacks['stop_thinking'] = callbacks['stop_thinking_animation']
        if 'is_currenlty_expanded' in callbacks:
            self.state_manager_callbacks['is_currenlty_expanded']  = callbacks['is_currenlty_expanded']
        if 'multiline_toggle_clicked' in callbacks:
            # Store the callback and connect to debounced handler
            self.pending_multiline_callback = callbacks['multiline_toggle_clicked']
            self.multiline_toggle_button.clicked.connect(self._handle_multiline_toggle_click)


    def update_multiline_toggle_button(self, is_multiline):
        """Update multiline toggle button appearance based on current state."""
        if is_multiline:
            self.multiline_toggle_button.setText("📝")  # Multi-line icon
            self.multiline_toggle_button.setToolTip("Switch to single-line input")
            self.multiline_toggle_button.setObjectName("multilineToggleButtonActive")
        else:
            self.multiline_toggle_button.setText("📄")  # Single-line icon  
            self.multiline_toggle_button.setToolTip("Switch to multi-line input")
            self.multiline_toggle_button.setObjectName("multilineToggleButton")
        
        # Force style update
        self.multiline_toggle_button.style().unpolish(self.multiline_toggle_button)
        self.multiline_toggle_button.style().polish(self.multiline_toggle_button)
  
    def _handle_multiline_toggle_click(self):
        """Handle multiline toggle with debouncing."""
        # Reset timer and start new one
        self.multiline_toggle_debounce_timer.stop()
        self.multiline_toggle_debounce_timer.start(100)  # 100ms debounce

    def _handle_multiline_toggle_debounced(self):
        """Execute the actual multiline toggle callback after debounce."""
        if self.pending_multiline_callback:
            self.pending_multiline_callback()

    def set_input_text(self, text):
        """Set text in input field regardless of type."""
        if hasattr(self.input_field, 'setPlainText'):
            self.input_field.setPlainText(text)
        else:
            self.input_field.setText(text)

    def get_input_text(self):
        """Get text from input field regardless of type."""
        if hasattr(self.input_field, 'toPlainText'):
            return self.input_field.toPlainText()
        else:
            return self.input_field.text()

    def clear_input(self):
        """Clear input field and reset heights."""
        if hasattr(self.input_field, 'clear'):
            self.input_field.clear()
            
        # Reset to original heights when clearing in multiline mode
        if self.multiline_input:
            self._reset_input_and_window_height()

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
        """Set visual state of input field: 'normal', 'thinking' """
        if state == "typing":
            if 'stop_thinking' in self.animation_callbacks:
                self.animation_callbacks['stop_thinking']()
            self.input_field.setObjectName("inputFieldTyping")
            self.input_field.setStyle(self.input_field.style())
        elif state == "thinking":
            self.input_field.setObjectName("inputFieldThinking")
            if 'start_thinking' in self.animation_callbacks:
                self.animation_callbacks['start_thinking'](self.input_field)
        else:  # normal
            if 'stop_thinking' in self.animation_callbacks:
                self.animation_callbacks['stop_thinking']()
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

    def reset_input_height(self):
        """Reset input field to original single-line height."""
        pass
        # if self.multiline_input and self.original_input_height:
        #     self.input_field.setMinimumHeight(self.original_input_height)
        #     self.input_field.setMaximumHeight(self.original_input_height)
            
        #     # Reset window height too
        #     if self.original_window_height:
        #         self.parent.animate_resize(self.parent.width(), self.original_window_height, fast=True)



    def recreate_input_field(self, multiline_input):
        """Recreate input field when mode changes."""
        if self.input_field:
            # Store current text
            if hasattr(self.input_field, 'toPlainText'):
                current_text = self.input_field.toPlainText()
            else:
                current_text = self.input_field.text()

            is_currently_window_expanded = False
            if 'is_currenlty_expanded' in self.state_manager_callbacks:
                is_currently_window_expanded = self.state_manager_callbacks['is_currenlty_expanded']()
            
            # Reset to original window height if switching from multiline
            if self.multiline_input and not multiline_input and self.original_window_height and not is_currently_window_expanded:
                self.parent.animate_resize(self.parent.width(), self.original_window_height, fast=True)
            
            # Remove old input field
            layout = self.input_field.parent().layout()
            layout.removeWidget(self.input_field)
            self.input_field.deleteLater()
            
            # Reset height tracking when switching modes
            # self.original_input_height = None
            if not multiline_input:  # Only reset window height when going to single-line
                self.original_window_height = None
            
            # Update mode and create new field
            self.multiline_input = multiline_input
            self._create_input_field()
            
            # Store original heights for new multiline mode
            if multiline_input:
                self._store_original_heights()
            
            # Insert new field at the beginning of the layout
            layout.insertWidget(0, self.input_field)
            
            # Restore text (this might trigger resize)
            if hasattr(self.input_field, 'setText'):
                self.input_field.setText(current_text)
            elif hasattr(self.input_field, 'setPlainText'):
                self.input_field.setPlainText(current_text)

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

        # Create input field based on multiline setting
        self._create_input_field()
        input_layout.addWidget(self.input_field)

        # Multiline toggle button
        self.multiline_toggle_button = QPushButton()
        self.multiline_toggle_button.setFixedSize(
            ElementSize.SETTINGS_BUTTON_SIZE, ElementSize.SETTINGS_BUTTON_SIZE)
        self.multiline_toggle_button.setFont(QFont("Segoe UI Emoji", 14))  # Larger emoji font
        self.update_multiline_toggle_button(self.multiline_input)
        input_layout.addWidget(self.multiline_toggle_button)

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

        self._setup_emoji_font(self.response_area)
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


    def _create_input_field(self):
        """Create appropriate input field based on multiline setting."""
        if self.multiline_input:
            # Multi-line input
            self.input_field = QTextEdit()
            self.input_field.setPlaceholderText(f"{Text.INPUT_PLACEHOLDER}\n(Ctrl+Enter to send)")
            
            # Set initial height to single line equivalent
            font_metrics = self.input_field.fontMetrics()
            single_line_height = font_metrics.height()  # 30px for padding
            # self.input_field.setMinimumHeight(single_line_height)
            # self.input_field.setMaximumHeight(single_line_height)
            
            # Store original heights
            self.original_input_height = single_line_height
            if self.original_window_height is None:
                self.original_window_height = self.parent.height()
            
            self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.input_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # Connect to content change to handle resizing
            self.input_field.textChanged.connect(self._handle_multiline_resize)
            
        else:
            # Single-line input
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText(f"{Text.INPUT_PLACEHOLDER} (Enter to send)")
        
        self.input_field.setObjectName("inputField")

    def _handle_multiline_resize(self):
        """Handle resizing of multiline input field and window based on content."""
        if not self.multiline_input or not hasattr(self.input_field, 'document'):
            return
        
        text = self.input_field.toPlainText()
        if text.strip() == "":
            return
        # Count actual lines in the text
        line_count = max(1, text.count('\n') + 1)  # At least 1 line

        new_input_height_cal = (line_count * InputSettings.LINE_HEIGHT) + InputSettings.BASE_PADDING
        
        new_input_height = min(new_input_height_cal, InputSettings.MAX_HEIGHT)
        
        # Update input field height
        self.input_field.setMinimumHeight(new_input_height)
        self.input_field.setMaximumHeight(new_input_height)
        
        is_currently_window_expanded = False
        if 'is_currenlty_expanded' in self.state_manager_callbacks:
                is_currently_window_expanded = self.state_manager_callbacks['is_currenlty_expanded']()

        # Calculate new window height
        if self.original_window_height and not is_currently_window_expanded:
            # Base window expansion on number of lines beyond the first line
            extra_lines = max(0, line_count - 1)
            window_height_increase = extra_lines * InputSettings.LINE_HEIGHT
            new_window_height = self.original_window_height + window_height_increase
            
            # Ensure reasonable bounds
            min_height = self.min_window_height
            max_height = min_height + 300  # Allow substantial expansion
            new_window_height = max(min_height, min(new_window_height, max_height))
            
            # Only resize window if height actually changed
            current_window_height = self.parent.height()
            if abs(new_window_height - current_window_height) > 5:  # 5px tolerance
                self.logger.debug(f"Resizing window: {current_window_height} -> {new_window_height} (lines: {line_count})")
                self.parent.animate_resize(self.parent.width(), new_window_height, fast=True)

    def _setup_emoji_font(self, widget):
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

    def _store_original_heights(self):
        """Store original heights when first entering multiline mode."""
        if self.original_window_height is None:
            self.original_window_height = self.parent.height()
            self.logger.debug(f"Stored original window height: {self.original_window_height}")

    def _reset_input_and_window_height(self):
        """Reset both input field and window to original heights."""
        if self.multiline_input and self.original_input_height and self.original_window_height:
            self.logger.debug(f"Resetting heights - Input: {self.original_input_height}, Window: {self.original_window_height}")
            
            # Reset input field height
            self.input_field.setMinimumHeight(self.original_input_height)
            self.input_field.setMaximumHeight(self.original_input_height)
            
            # Reset window height
            current_window_height = self.parent.height()
            if abs(self.original_window_height - current_window_height) > 5:  # 5px tolerance
                self.parent.animate_resize(self.parent.width(), self.original_window_height, fast=True)