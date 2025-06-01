import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
                             QPushButton, QTextBrowser, QFrame, QShortcut,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QFontDatabase
from utils.constants import (
    ElementSize, Files, InputSettings, Text, WindowSize)


class UIManager(QObject):

    expansion_changed = pyqtSignal(bool)
    visual_state_changed = pyqtSignal(str)

    def __init__(self, parent_window, logger, config):
        super().__init__()
        self.parent = parent_window
        self.logger = logger.getChild('ui_manager')
        self.config = config

        self.main_container = None
        self.input_field = None
        self.response_area = None
        self.stt_button = None
        self.settings_button = None
        self.copy_button = None
        self.input_type_is_multiline = False
        self.multiline_toggle_button = None

        self.original_input_height = None
        self.original_window_height = None
        self.min_window_height = WindowSize.COMPACT_HEIGHT
        self.animation_callbacks = {}
        self.state_manager_callbacks = {}

        self.current_visual_state = "normal"
        self.is_expanded = False
        self.response_visible = False

    def setup_ui(self, multiline_input=False):
        """Create and setup all UI components."""
        self.input_type_is_multiline = multiline_input
        self._create_main_container()
        self._create_input_section()
        self._create_response_section()
        self._create_copy_button()
        self._setup_shortcuts()

    def connect_signals(self, callbacks):
        """Connect UI signals to callbacks."""

        self._disconnect_all_signals()

        if 'input_changed' in callbacks:
            if hasattr(self.input_field, 'toPlainText'):
                # QTextEdit - textChanged doesn't pass text
                self.input_field.textChanged.connect(
                    lambda: callbacks['input_changed'](self.get_input_text()))
            else:
                # QLineEdit - textChanged passes text
                self.input_field.textChanged.connect(
                    callbacks['input_changed'])
        if 'return_pressed' in callbacks:
            # Install event filter on parent to handle key events
            self.input_field.installEventFilter(self.parent)
        if 'stt_clicked' in callbacks:
            self.stt_button.clicked.connect(callbacks['stt_clicked'])
        if 'settings_clicked' in callbacks:
            self.settings_button.clicked.connect(callbacks['settings_clicked'])
        if 'copy_clicked' in callbacks:
            self.copy_button.clicked.connect(callbacks['copy_clicked'])
        if 'start_thinking_animation' in callbacks:
            self.animation_callbacks['start_thinking'] = callbacks['start_thinking_animation']
        if 'stop_thinking_animation' in callbacks:
            self.animation_callbacks['stop_thinking'] = callbacks['stop_thinking_animation']
        if 'is_currenlty_expanded' in callbacks:
            self.state_manager_callbacks['is_currenlty_expanded'] = callbacks['is_currenlty_expanded']

        self.multiline_toggle_button.clicked.connect(self._toggle_input_type)

    def connect_input_signals(self, callbacks):
        """Connect UI signals to callbacks."""
        
        self._disconnect_input_signals()

        if 'input_changed' in callbacks:
            if hasattr(self.input_field, 'toPlainText'):
                # QTextEdit - textChanged doesn't pass text
                self.input_field.textChanged.connect(
                    lambda: callbacks['input_changed'](self.get_input_text()))
            else:
                # QLineEdit - textChanged passes text
                self.input_field.textChanged.connect(
                    callbacks['input_changed'])
        if 'return_pressed' in callbacks:
            # Install event filter on parent to handle key events
            self.input_field.installEventFilter(self.parent)

#   ##########################################################################################
#       UI Functions
#   ##########################################################################################

    def expand_ui(self):
        """Expand UI to show response area - alias for show_response_area."""
        self.show_response_area()

    def _apply_visual_state(self, state):
        """Apply visual changes based on state."""
        if state == "thinking":
            self.input_field.setObjectName("inputFieldThinking")
            if 'start_thinking' in self.animation_callbacks:
                self.animation_callbacks['start_thinking'](self.input_field)
        else:
            if state == "typing":
                if 'stop_thinking' in self.animation_callbacks:
                    self.animation_callbacks['stop_thinking']()
                self.input_field.setObjectName("inputFieldTyping")
            elif state == "thinking":
                self.input_field.setObjectName("inputFieldThinking")
                if 'start_thinking' in self.animation_callbacks:
                    self.animation_callbacks['start_thinking'](
                        self.input_field)
            elif state == "error":
                if 'stop_thinking' in self.animation_callbacks:
                    self.animation_callbacks['stop_thinking']()
                self.input_field.setObjectName("inputFieldError")
            else:  # normal
                if 'stop_thinking' in self.animation_callbacks:
                    self.animation_callbacks['stop_thinking']()
                self.input_field.setObjectName("inputField")
            self.input_field.setStyle(self.input_field.style())

#   ##########################################################################################
#       Window Functions
#   ##########################################################################################

    def _store_original_heights(self):
        """Store original heights when first entering multiline mode."""
        if self.original_window_height is None:
            self.original_window_height = self.parent.height()
            self.logger.debug(
                f"Stored original window height: {self.original_window_height}")

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

#   ##########################################################################################
#       Input Field Functions
#   ##########################################################################################

    def get_input_text(self):
        """Get text from input field regardless of type."""
        if hasattr(self.input_field, 'toPlainText'):
            return self.input_field.toPlainText()
        else:
            return self.input_field.text()

    def handle_multiline_resize(self):
        """Handle resizing of multiline input field and window based on content."""
        self.logger.debug("Starting multiline resize handling")

        if not self.input_type_is_multiline or not hasattr(self.input_field, 'document'):
            self.logger.debug("Skipping resize: input_type_is_multiline=%s, has_document=%s",
                              self.input_type_is_multiline, hasattr(self.input_field, 'document'))
            return

        try:
            text = self.input_field.toPlainText()
            self.logger.debug("Processing text with length: %d", len(text))

            # Calculate actual displayed lines including wrapped text
            document = self.input_field.document()
            document_layout = document.documentLayout()

            # Get the width available for text (excluding margins/padding)
            text_width = self.input_field.viewport().width()
            self.logger.debug("Text viewport width: %d pixels", text_width)

            # Calculate total visual lines (including wrapped lines)
            total_visual_lines = 0
            block = document.firstBlock()
            block_count = 0

            while block.isValid():
                block_count += 1
                block_layout = block.layout()

                if block_layout:
                    # Count line breaks within this block (wrapped lines)
                    line_count_in_block = block_layout.lineCount()
                    # At least 1 line per block
                    lines_added = max(1, line_count_in_block)
                    total_visual_lines += lines_added
                    self.logger.debug("Block %d: layout lines=%d, added=%d",
                                      block_count, line_count_in_block, lines_added)
                else:
                    # Fallback: estimate wrapped lines based on text length and width
                    block_text = block.text()
                    if not block_text:
                        total_visual_lines += 1  # Empty line
                        self.logger.debug("Block %d: empty line", block_count)
                    else:
                        try:
                            font_metrics = self.input_field.fontMetrics()
                            text_width_pixels = font_metrics.horizontalAdvance(
                                block_text)
                            estimated_lines = max(
                                1, (text_width_pixels // max(1, text_width)) + 1)
                            total_visual_lines += estimated_lines
                            self.logger.debug("Block %d: fallback estimation - text_width_pixels=%d, estimated_lines=%d",
                                              block_count, text_width_pixels, estimated_lines)
                        except Exception as e:
                            self.logger.error(
                                "Error calculating fallback line estimation for block %d: %s", block_count, e)
                            total_visual_lines += 1  # Safe fallback

                block = block.next()

            self.logger.debug(
                "Processed %d blocks, total visual lines: %d", block_count, total_visual_lines)

            # Ensure at least 1 line
            line_count = max(1, total_visual_lines)
            new_input_height_cal = (
                line_count * InputSettings.LINE_HEIGHT) + InputSettings.BASE_PADDING
            new_input_height = min(new_input_height_cal,
                                   InputSettings.MAX_HEIGHT)

            self.logger.debug("Input height calculation: lines=%d, calculated=%d, final=%d (max=%d)",
                              line_count, new_input_height_cal, new_input_height, InputSettings.MAX_HEIGHT)

            # Update input field height
            self.input_field.setMinimumHeight(new_input_height)
            self.input_field.setMaximumHeight(new_input_height)
            self.logger.debug(
                "Updated input field height to: %d", new_input_height)

            is_currently_window_expanded = False
            if 'is_currenlty_expanded' in self.state_manager_callbacks:
                try:
                    is_currently_window_expanded = self.state_manager_callbacks['is_currenlty_expanded'](
                    )
                    self.logger.debug("Window expansion state: %s",
                                      is_currently_window_expanded)
                except Exception as e:
                    self.logger.error(
                        "Error checking window expansion state: %s", e)

            # Calculate new window height
            if self.original_window_height and not is_currently_window_expanded:
                self.logger.debug(
                    "Calculating window resize - original_height=%d", self.original_window_height)

                # Base window expansion on number of lines beyond the first line
                extra_lines = max(0, line_count - 1)
                window_height_increase = extra_lines * InputSettings.LINE_HEIGHT
                new_window_height = self.original_window_height + window_height_increase

                self.logger.debug("Window height calculation: extra_lines=%d, increase=%d, new_height=%d",
                                  extra_lines, window_height_increase, new_window_height)

                # Ensure reasonable bounds
                min_height = self.min_window_height
                max_height = min_height + 300  # Allow substantial expansion
                new_window_height = max(min_height, min(
                    new_window_height, max_height))

                self.logger.debug("Window height bounds: min=%d, max=%d, bounded_height=%d",
                                  min_height, max_height, new_window_height)

                # Only resize window if height actually changed
                current_window_height = self.parent.height()
                height_difference = abs(
                    new_window_height - current_window_height)

                if height_difference > 5:  # 5px tolerance
                    self.logger.debug("Resizing window: %d -> %d (difference: %d, lines: %d)",
                                      current_window_height, new_window_height, height_difference, line_count)
                    try:
                        self.parent.animate_resize(
                            self.parent.width(), new_window_height, fast=True)
                        self.logger.debug(
                            "Window resize animation started successfully")
                    except Exception as e:
                        self.logger.error(
                            "Error during window resize animation: %s", e)
                else:
                    self.logger.debug(
                        "Skipping window resize - difference too small: %d pixels", height_difference)
            else:
                if not self.original_window_height:
                    self.logger.debug(
                        "Skipping window resize - no original_window_height set")
                if is_currently_window_expanded:
                    self.logger.debug(
                        "Skipping window resize - window is currently expanded")

            if self.response_area.isVisible():
                self.logger.debug("Scheduling copy button positioning")
                QTimer.singleShot(10, self.position_copy_button)
            else:
                self.logger.debug(
                    "Response area not visible, skipping copy button positioning")

        except Exception as e:
            self.logger.error(
                "Unexpected error in handle_multiline_resize: %s", e, exc_info=True)

    def is_multiline_input(self):
        return self.input_type_is_multiline

    def reset_input_height(self):
        """Reset input field to original single-line height."""
        pass

    def recreate_input_field(self, is_multiline_input):
        """Recreate input field when mode changes."""
        if self.input_field:
            # Store current text
            if hasattr(self.input_field, 'toPlainText'):
                current_text = self.input_field.toPlainText()
            else:
                current_text = self.input_field.text()

            is_currently_window_expanded = False
            if 'is_currenlty_expanded' in self.state_manager_callbacks:
                is_currently_window_expanded = self.state_manager_callbacks['is_currenlty_expanded'](
                )
            else:
                self.logger.error(
                    "Error accessing callback: is_currenlty_expanded")

            # Reset to original window height if switching from multiline
            if self.input_type_is_multiline and not is_multiline_input and self.original_window_height and not is_currently_window_expanded:
                self.parent.animate_resize(
                    self.parent.width(), self.original_window_height, fast=True)

            # Get the layout and find the old input field's position
            layout = self.input_field.parent().layout()
            old_input_field = self.input_field

            # Reset height tracking when switching modes
            if not is_multiline_input:  # Only reset window height when going to single-line
                self.original_window_height = None

            # Update mode and create new field
            self.input_type_is_multiline = is_multiline_input
            self._create_input_field()

            # Store original heights for new multiline mode
            if is_multiline_input:
                self._store_original_heights()

            # Replace the widget in the layout (maintains position)
            layout.replaceWidget(old_input_field, self.input_field)
            old_input_field.deleteLater()

            # Restore text (this might trigger resize)
            if hasattr(self.input_field, 'setText'):
                self.input_field.setText(current_text)
            elif hasattr(self.input_field, 'setPlainText'):
                self.input_field.setPlainText(current_text)

            # If multiline resize based on the text
            if is_multiline_input:
                self.handle_multiline_resize()

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

    def set_input_text(self, text):
        """Set text in input field regardless of type."""
        if hasattr(self.input_field, 'setPlainText'):
            self.input_field.setPlainText(text)
        else:
            self.input_field.setText(text)

    def set_input_type(self, is_multiline):
        """Set input type and handle UI changes"""
        if self.input_type_is_multiline == is_multiline:
            return

        self.input_type_is_multiline = is_multiline
        self.update_multiline_toggle_button(is_multiline)
        self.recreate_input_field(is_multiline)

        # Save to config
        self.config.set('multiline_input', is_multiline)

        if hasattr(self.parent, 'on_input_type_changed'):
            self.parent.on_input_type_changed()

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
        self.multiline_toggle_button.setFont(
            QFont("Segoe UI Emoji", 14))  # Larger emoji font
        self.update_multiline_toggle_button(self.input_type_is_multiline)
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

    def _disconnect_all_signals(self):
        """Disconnect all signals before reconnecting"""
        try:
            # Disconnect input field signals safely
            if hasattr(self.input_field, 'textChanged'):
                try:
                    self.input_field.textChanged.disconnect()
                except TypeError:
                    pass  # No connections to disconnect

            # Disconnect button signals safely
            if hasattr(self.stt_button, 'clicked'):
                try:
                    self.stt_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.settings_button, 'clicked'):
                try:
                    self.settings_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.copy_button, 'clicked'):
                try:
                    self.copy_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.multiline_toggle_button, 'clicked'):
                try:
                    self.multiline_toggle_button.clicked.disconnect()
                except TypeError:
                    pass
        except Exception as e:
            self.logger.error(f"Error disconnecting signals: {e}")

    def _disconnect_input_signals(self):
        """Disconnect all signals before reconnecting"""
        try:
            # Disconnect input field signals safely
            if hasattr(self.input_field, 'textChanged'):
                try:
                    self.input_field.textChanged.disconnect()
                except TypeError:
                    pass  # No connections to disconnect
        except Exception as e:
            self.logger.error(f"Error disconnecting signals: {e}")

    def _create_input_field(self):
        """Create appropriate input field based on multiline setting."""
        if self.input_type_is_multiline:
            # Multi-line input
            self.input_field = QTextEdit()
            self.input_field.setPlaceholderText(
                f"{Text.INPUT_PLACEHOLDER} (Ctrl+Enter to send)")

            # Set initial height to single line equivalent
            font_metrics = self.input_field.fontMetrics()
            single_line_height = font_metrics.height()

            # Store original heights
            self.original_input_height = single_line_height
            if self.original_window_height is None:
                self.original_window_height = self.parent.height()

            self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.input_field.setHorizontalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff)

        else:
            # Single-line input
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText(
                f"{Text.INPUT_PLACEHOLDER} (Enter to send)")

        self.input_field.setObjectName("inputField")

    def _toggle_input_type(self):
        """Toggle between single-line and multi-line input"""
        self.set_input_type(not self.input_type_is_multiline)

#   ##########################################################################################
#       Response Area Functions
#   ##########################################################################################

    def show_response_area(self):
        """Show response area and copy button."""
        if not self.response_visible:
            self.response_area.setVisible(True)
            self.response_visible = True
            self.is_expanded = True
            self.expansion_changed.emit(True)
            # self.copy_button.setVisible(True)
            self.logger.debug("Response area shown")
            self.position_copy_button()

    def hide_response(self):
        """
        Hide response area and copy button.
        This is purely UI logic - hiding/showing widgets and managing layout.
        """
        if self.response_visible:
            # self.response_area.setVisible(False)
            self.copy_button.setVisible(False)
            self.response_visible = False
            self.is_expanded = False
            self.expansion_changed.emit(False)
            # self.parent.animate_resize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT, fast=True)
            QTimer.singleShot(50, lambda: self.response_area.setVisible(False))
            self.logger.debug("Response area hidden")

    def is_response_visible(self):
        return self.response_visible

    def toggle_response_visibility(self):
        """Toggle response area visibility."""
        if self.response_visible:
            self.hide_response()
        else:
            self.show_response_area()

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

#   ##########################################################################################
#       Button Functions
#   ##########################################################################################

    def position_copy_button(self):
        """Position copy button in response area."""
        if self.response_area.isVisible():
            response_pos = self.response_area.pos()
            response_geometry = self.response_area.geometry()

            self.logger.debug(
                f"Response area position: {response_pos}, geometry: {response_geometry}")

            button_x = (response_pos.x() + response_geometry.width() -
                        self.copy_button.width() - ElementSize.SCROLLBAR_SIZE -
                        ElementSize.COPY_BUTTON_RIGHT_MARGIN)
            button_y = response_pos.y() + ElementSize.COPY_BUTTON_RIGHT_MARGIN

            self.logger.debug(
                f"Calculated copy button position: x={button_x}, y={button_y}")

            self.copy_button.move(button_x, button_y)
            self.copy_button.raise_()
            self.copy_button.setVisible(True)

            self.logger.debug("Copy button positioned and made visible")
        else:
            self.logger.debug(
                "Response area not visible, copy button not positioned")

    def update_stt_button_appearance(self, state):
        """Update STT button appearance."""
        if state == "recording":
            self.stt_button.setIcon(QIcon(str(Files.MIC_RECORDING_ICON_PATH)))
        else:
            self.stt_button.setIcon(QIcon(str(Files.MIC_IDLE_ICON_PATH)))

        self.stt_button.style().unpolish(self.stt_button)
        self.stt_button.style().polish(self.stt_button)

    def update_stt_button_visibility(self, enabled):
        """Update STT button visibility."""
        self.stt_button.setVisible(enabled)
        self.stt_button.setEnabled(enabled)

    def update_multiline_toggle_button(self, is_multiline):
        """Update multiline toggle button appearance based on current state."""
        if is_multiline:
            self.multiline_toggle_button.setText("📝")  # Multi-line icon
            self.multiline_toggle_button.setToolTip(
                "Switch to single-line input")
            self.multiline_toggle_button.setObjectName(
                "multilineToggleButtonActive")
        else:
            self.multiline_toggle_button.setText("📄")  # Single-line icon
            self.multiline_toggle_button.setToolTip(
                "Switch to multi-line input")
            self.multiline_toggle_button.setObjectName("multilineToggleButton")

        # Force style update
        self.multiline_toggle_button.style().unpolish(self.multiline_toggle_button)
        self.multiline_toggle_button.style().polish(self.multiline_toggle_button)

    def _create_copy_button(self):
        """Create copy button."""
        self.copy_button = QPushButton(Text.COPY_BUTTON)
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setFixedSize(
            ElementSize.COPY_BUTTON_WIDTH, ElementSize.COPY_BUTTON_HEIGHT)
        self.copy_button.setVisible(False)
        self.copy_button.setParent(self.main_container)
        self.copy_button.raise_()

#   ##########################################################################################
#       State Functions
#   ##########################################################################################

    def set_visual_state(self, state):
        """Set visual state of UI components."""
        self.logger.debug(f"Set visual state: {state}")
        if self.current_visual_state != state:
            old_state = self.current_visual_state
            self.current_visual_state = state
            self.logger.debug(
                f"Visual state changed from '{old_state}' to '{state}'")

            # Apply visual changes immediately
            self._apply_visual_state(state)
            self.visual_state_changed.emit(state)

    def get_visual_state(self):
        return self.current_visual_state

    # Getters for UI state
    def is_currently_expanded(self):
        """Check if UI is currently expanded."""
        return self.is_expanded

#   ##########################################################################################
#       Help Functions
#   ##########################################################################################

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

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # ESC to hide to tray
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self.parent)
        escape_shortcut.activated.connect(self.parent.hide_window)

        # Ctrl+Q to quit completely
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self.parent)
        quit_shortcut.activated.connect(self.parent.quit_application)
