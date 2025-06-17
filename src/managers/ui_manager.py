import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
                             QPushButton, QTextBrowser, QFrame, QShortcut, QLabel,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QFontDatabase
from managers.style_manager import StyleManager
from utils.constants import (
    ElementSize, Files, InputSettings, Text, WindowSize)
from utils.markdown_render import MarkdownRenderer
from widgets.conversation_history_widget import ConversationHistoryWidget
from widgets.conversation_widget import ConversationWidget
from widgets.error_message import ErrorMessage


class UIManager(QObject):

    expansion_changed = pyqtSignal(bool)
    visual_state_changed = pyqtSignal(str)

    def __init__(self, parent_window, config, style_manager:StyleManager):
        super().__init__()
        self.parent = parent_window
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.style_manager = style_manager

        # UI Components
        self.main_container = None
        self.input_field = None
        self.conversation_widget = None  # Changed from conversation_area
        self.stt_button = None
        self.settings_button = None
        self.multiline_toggle_button = None
        self.conversation_toggle_button = None
        self.error_message = None
        self.conversation_history_button = None
        self.conversation_history_widget = None
        
        # State
        self.input_type_is_multiline = False
        self.original_window_height = None
        self.min_window_height = WindowSize.COMPACT_HEIGHT
        self.animation_callbacks = {}
        self.current_visual_state = "normal"
        self.is_expanded = False
        self.conversation_visible = False
        
        # Managers
        self.markdown_render = MarkdownRenderer(self.style_manager)

    def setup_ui(self, conversation_manager):
        """Create and setup all UI components."""
        is_multiline = self.config.get(
            'multiline_input', InputSettings.IS_MULTILINE_INPUT)
        self.input_type_is_multiline = is_multiline
        self.conversation_manager = conversation_manager
        self._create_main_container()
        self._create_input_section()
        self._create_response_section()
        self._create_conversation_toggle_button()
        self._setup_shortcuts()

        self._create_conversation_history_button()
        self._create_conversation_history_widget()  

        self.conversation_widget.set_conversation_manager(conversation_manager)

    def connect_signals(self, callbacks):
        """Connect UI signals to callbacks."""
        self._disconnect_all_signals()
        
        # Input field signals
        if 'input_changed' in callbacks:
            if hasattr(self.input_field, 'toPlainText'):
                self.input_field.textChanged.connect(
                    lambda: callbacks['input_changed'](self.get_input_text()))
            else:
                self.input_field.textChanged.connect(callbacks['input_changed'])
        
        if 'return_pressed' in callbacks:
            self.input_field.installEventFilter(self.parent)
        
        # Button signals
        if 'stt_clicked' in callbacks:
            self.stt_button.clicked.connect(callbacks['stt_clicked'])
        if 'settings_clicked' in callbacks:
            self.settings_button.clicked.connect(callbacks['settings_clicked'])
        
        # Animation callbacks
        if 'start_thinking_animation' in callbacks:
            self.animation_callbacks['start_thinking'] = callbacks['start_thinking_animation']
        if 'stop_thinking_animation' in callbacks:
            self.animation_callbacks['stop_thinking'] = callbacks['stop_thinking_animation']
        
        self.conversation_history_button.clicked.connect(self.toggle_history_widget)
        self.multiline_toggle_button.clicked.connect(self._toggle_input_type)
        self.conversation_toggle_button.clicked.connect(self.toggle_response_visibility)

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
            text_width = self.input_field.viewport().width()
            self.logger.debug("Text viewport width: %d pixels", text_width)

            # [Your existing line counting logic here - this part looks correct]
            total_visual_lines = 0
            block = document.firstBlock()
            block_count = 0
            while block.isValid():
                block_count += 1
                block_layout = block.layout()
                if block_layout:
                    line_count_in_block = block_layout.lineCount()
                    lines_added = max(1, line_count_in_block)
                    total_visual_lines += lines_added
                    self.logger.debug("Block %d: layout lines=%d, added=%d",
                                    block_count, line_count_in_block, lines_added)
                else:
                    block_text = block.text()
                    if not block_text:
                        total_visual_lines += 1
                        self.logger.debug("Block %d: empty line", block_count)
                    else:
                        try:
                            font_metrics = self.input_field.fontMetrics()
                            text_width_pixels = font_metrics.horizontalAdvance(block_text)
                            estimated_lines = max(1, (text_width_pixels // max(1, text_width)) + 1)
                            total_visual_lines += estimated_lines
                            self.logger.debug("Block %d: fallback estimation - text_width_pixels=%d, estimated_lines=%d",
                                            block_count, text_width_pixels, estimated_lines)
                        except Exception as e:
                            self.logger.error("Error calculating fallback line estimation for block %d: %s", block_count, e)
                            total_visual_lines += 1
                block = block.next()

            line_count = max(1, total_visual_lines)
            new_input_height_cal = (line_count * InputSettings.LINE_HEIGHT) + InputSettings.BASE_PADDING
            new_input_height = min(new_input_height_cal, InputSettings.MAX_HEIGHT)
            
            # Update input field height
            self.input_field.setMinimumHeight(new_input_height)
            self.input_field.setMaximumHeight(new_input_height)
            self.logger.debug("Updated input field height to: %d", new_input_height)

            # **FIXED WINDOW HEIGHT CALCULATION**
            if not self.is_currently_expanded():
                self.logger.debug("Calculating window resize for non-expanded state")
                
                # Use WindowSize constants as base heights
                base_height = WindowSize.COMPACT_HEIGHT
                base_lines = 1  # Compact height is designed for 1 line
                
                # Calculate additional height needed for extra lines
                extra_lines = max(0, line_count - base_lines)
                window_height_increase = extra_lines * InputSettings.LINE_HEIGHT
                new_window_height = base_height + window_height_increase
                
                self.logger.debug("Window height calculation: base=%d, extra_lines=%d, increase=%d, new_height=%d",
                                base_height, extra_lines, window_height_increase, new_window_height)
                
                # Set reasonable bounds using WindowSize constants
                min_height = WindowSize.COMPACT_HEIGHT
                # Max height should not exceed multiline expanded height
                max_height = WindowSize.EXPANDED_MULTILINE_INPUT_HEIGHT
                new_window_height = max(min_height, min(new_window_height, max_height))
                
                self.logger.debug("Window height bounds: min=%d, max=%d, bounded_height=%d",
                                min_height, max_height, new_window_height)
                
                # Only resize if height actually changed
                current_window_height = self.parent.height()
                height_difference = abs(new_window_height - current_window_height)
                
                if height_difference > 5:  # 5px tolerance
                    self.logger.debug("Resizing window: %d -> %d (difference: %d, lines: %d)",
                                    current_window_height, new_window_height, height_difference, line_count)
                    try:
                        # Use WindowSize.COMPACT_WIDTH or current width
                        target_width = self.parent.width()  # Keep current width
                        self.parent.animate_resize(target_width, new_window_height, fast=True)
                        self.logger.debug("Window resize animation started successfully")
                    except Exception as e:
                        self.logger.error("Error during window resize animation: %s", e)
                else:
                    self.logger.debug("Skipping window resize - difference too small: %d pixels", height_difference)
            else:
                self.logger.debug("Window is expanded, skipping window resize")

        except Exception as e:
            self.logger.error("Unexpected error in handle_multiline_resize: %s", e, exc_info=True)

    def is_multiline_input(self):
        return self.input_type_is_multiline

    def recreate_input_field(self, is_multiline_input):
        """Recreate input field when mode changes."""
        if self.input_field:
            # Store current text
            if hasattr(self.input_field, 'toPlainText'):
                current_text = self.input_field.toPlainText()
            else:
                current_text = self.input_field.text()

            # Reset to original window height if switching from multiline
            if self.input_type_is_multiline and not is_multiline_input and self.original_window_height and not self.is_currently_expanded():
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
            QFont("Segoe UI Emoji", 14)) # Larger emoji font
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

    def update_conversation_toggle_button(self, is_expanded):
        """Update conversation toggle button appearance based on current state."""
        if not is_expanded:
            self.conversation_toggle_button.setText("▼")
            self.conversation_toggle_button.setToolTip("Hide conversation")
            self.conversation_toggle_button.setObjectName("conversationToggleButtonExpanded")
        else:
            self.conversation_toggle_button.setText("▲")
            self.conversation_toggle_button.setToolTip("Show conversation")
            self.conversation_toggle_button.setObjectName("conversationToggleButton")
        # Force style update
        self.conversation_toggle_button.style().unpolish(self.conversation_toggle_button)
        self.conversation_toggle_button.style().polish(self.conversation_toggle_button)

    def update_conversation_history_toggle_button(self):
        """Update conversation toggle button appearance based on current state."""
        if self.conversation_history_widget and self.conversation_history_widget.isVisible():
            self.conversation_history_button.setText("◀")
            self.conversation_history_button.setToolTip("Hide Conversation History")
            self.conversation_history_button.setObjectName("conversationToggleButtonExpanded")
        else:
            self.conversation_history_button.setText("▶")
            self.conversation_history_button.setToolTip("Show Conversation History")
            self.conversation_history_button.setObjectName("conversationToggleButton")
        # Force style update
        self.conversation_history_button.style().unpolish(self.conversation_history_button)
        self.conversation_history_button.style().polish(self.conversation_history_button)

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

            if hasattr(self.multiline_toggle_button, 'clicked'):
                try:
                    self.multiline_toggle_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.conversation_toggle_button, 'clicked'):  # Add this block
                try:
                    self.conversation_toggle_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.conversation_history_button, 'clicked'):
                try:
                    self.conversation_history_button.clicked.disconnect()
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

            # Store original heights
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

    def clear_conversation_area(self):
        self.conversation_widget.conversation_area.clear()

    def get_coversation_area_text(self):
        return self.conversation_widget.conversation_area.toPlainText()

    def auto_scroll(self):
        self.conversation_widget.auto_scroll()

    def show_error_in_conversation(self, error_message):
        """Show error message in conversation area."""
        try:
            error_text = f"<p style='color: red;'><strong>Error:</strong> {error_message}</p>"
            self.set_response_text(error_text)
            
            # Ensure conversation area is visible
            if not self.conversation_visible:
                self.show_conversation_area()
                
        except Exception as e:
            self.logger.error(f"Error showing error in conversation: {e}")

    def show_conversation_area(self):
        """Show response area and conversation widget."""
        if not self.conversation_visible:
            if self.is_multiline_input():
                self.handle_multiline_resize()
            
            self.response_container.setVisible(True)
            self.conversation_widget.setVisible(True)
            self.conversation_visible = True
            self.is_expanded = True
            self.expansion_changed.emit(True)
            self.update_conversation_toggle_button(True)
            self.update_conversation_history_toggle_button()
            self.conversation_history_button.setVisible(True)
            
            # Reposition the toggle button after expansion
            QTimer.singleShot(10, self.position_conversation_toggle_button)
            QTimer.singleShot(10, self.position_conversation_history_button)
            
            self.logger.debug("Response area shown")

    def hide_conversation_area(self):
        """Hide response area and conversation widget."""
        if self.conversation_visible:
            if self.is_multiline_input():
                self.handle_multiline_resize()
            
            self.conversation_visible = False
            self.is_expanded = False
            self.expansion_changed.emit(False)
            self.update_conversation_toggle_button(False)
            self.conversation_history_button.setVisible(False)
            self._hide_history_widget()
            
            QTimer.singleShot(10, self.position_conversation_toggle_button)
            QTimer.singleShot(50, lambda: self.response_container.setVisible(False))
            self.logger.debug("Response area hidden")

    def toggle_response_visibility(self):
        """Toggle response area visibility."""
        self.logger.debug(f"toggle_response_visibility, conversation is: {self.conversation_visible}")
        if self.conversation_visible:
            self.hide_conversation_area()
        else:
            self.show_conversation_area()

    def reapply_conversation_history_theme(self):
        self.conversation_widget.reapply_conversation_history_theme()

    def set_response_text(self, text):
        """Set response text - now aware of history mode."""
        self.conversation_widget.set_response_text(text)

    def is_showing_history(self):
        """Check if currently showing conversation history."""
        return self.conversation_widget.show_history_mode


    def append_response_text(self, text):
        """Append text to response - only works in current response mode."""
        if not self.conversation_widget.show_history_mode:
            current = self.conversation_widget.conversation_area.toHtml()
            self.conversation_widget.conversation_area.setHtml(current + text)
            # self._current_response = self.conversation_widget.conversation_area.toHtml()

    def get_current_response_text(self):
        """Get the current response text."""
        return getattr(self, '_current_response', '')

    def _escape_html(self, text):
        """Escape HTML characters in text content."""
        import html
        return html.escape(str(text)).replace('\n', '<br>')

    def is_conversation_visible(self):
        return self.conversation_visible


    def _create_response_section(self):
        """Create response section with conversation widget."""
        container_layout = self.main_container.layout()
        
        # Create conversation widget
        self.conversation_widget = ConversationWidget(
            style_manager=self.style_manager,
            parent=self.main_container
        )
        
        # Connect conversation widget signals
        self.conversation_widget.copy_requested.connect(self._handle_copy_request)
        
        # Create response container to manage visibility
        self.response_container = QWidget()
        response_layout = QVBoxLayout(self.response_container)
        response_layout.setContentsMargins(0, 0, 0, 0)
        response_layout.addWidget(self.conversation_widget)
        
        # Hide initially
        self.response_container.setVisible(False)
        self.conversation_widget.setVisible(False)
        
        container_layout.addWidget(self.response_container)
        container_layout.setStretchFactor(container_layout.itemAt(0).layout(), 0)  # Input section
        container_layout.setStretchFactor(self.response_container, 1)  # Response area
        container_layout.addStretch()

    def _handle_copy_request(self):
        """Handle copy request from conversation widget."""
        # This will be connected to the main copy callback
        if hasattr(self, '_copy_callback') and self._copy_callback:
            self._copy_callback()


#   ##########################################################################################
#       Button Functions
#   ##########################################################################################

    def position_conversation_toggle_button(self):
        """Position the conversation toggle button at the bottom edge of the window."""
        if not self.conversation_toggle_button or not self.main_container:
            self.logger.debug("Conversation Toggle Button not positioned")
            return
        try:
            # Get container dimensions
            container_geometry = self.main_container.geometry()
            button_width = self.conversation_toggle_button.width()
            button_height = self.conversation_toggle_button.height()
            
            # Position at bottom center, slightly inset from the edge
            x = (container_geometry.width() - button_width) // 2  # Center horizontally
            y = container_geometry.height() - button_height - 2   # 2px from bottom edge
            
            self.conversation_toggle_button.move(x, y)
            self.logger.debug(f"Main container geometry: x:{container_geometry.width()}, y:{container_geometry.height()}")
            self.logger.debug(f"Conversation toggle button positioned at ({x}, {y})")
            
        except Exception as e:
            self.logger.error(f"Error positioning conversation toggle button: {e}")

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

    def _create_conversation_toggle_button(self):
        """Create the conversation toggle button as a floating element at bottom edge."""
        self.conversation_toggle_button = QPushButton()
        self.conversation_toggle_button.setParent(self.main_container)
        self.conversation_toggle_button.setFixedSize(ElementSize.CONVERSATION_TOGGLE_BUTTON_WIDTH, ElementSize.CONVERSATION_TOGGLE_BUTTON_HEIGHT)
        self.conversation_toggle_button.setFont(QFont("Segoe UI", 5))
        self.update_conversation_toggle_button(self.conversation_visible)
        self.conversation_toggle_button.raise_()
        QTimer.singleShot(50, self.position_conversation_toggle_button)

    def update_stt_button_appearance(self, state):
        """Update STT button appearance based on state."""
        # self.ui_manager.stt_button.setStyle(self.ui_manager.stt_button.style())
        if state == "recording":
            self.stt_button.setIcon(QIcon(str(Files.MIC_RECORDING_ICON_PATH)))
            self.stt_button.style().unpolish(self.stt_button)
            self.stt_button.style().polish(self.stt_button)
        elif state == "idle":
            self.stt_button.setIcon(QIcon(str(Files.MIC_IDLE_ICON_PATH)))
            self.stt_button.style().unpolish(self.stt_button)
            self.stt_button.style().polish(self.stt_button)

    def _create_conversation_history_button(self):
        """Create the conversation history button as a floating element on the right side."""
        self.conversation_history_button = QPushButton()
        self.conversation_history_button.setParent(self.main_container)
        self.conversation_history_button.setFixedSize(
            ElementSize.CONVERSATION_TOGGLE_BUTTON_HEIGHT,  # Use height as width for square button
            ElementSize.CONVERSATION_TOGGLE_BUTTON_WIDTH
        )
        self.conversation_history_button.setFont(QFont("Segoe UI", 5))
        self.update_conversation_history_toggle_button()
        self.conversation_history_button.setToolTip("Show conversation history")
        self.conversation_history_button.setObjectName("conversationHistoryButton")
        
        # Hide initially (only show when expanded)
        self.conversation_history_button.setVisible(False)
        self.conversation_history_button.raise_()
        
        QTimer.singleShot(50, self.position_conversation_history_button)

    def position_conversation_history_button(self):
        """Position the conversation history button at the right middle of the window."""
        if not self.conversation_history_button or not self.main_container:
            self.logger.debug("Conversation History Button not positioned")
            return
        try:
            # Get container dimensions
            container_geometry = self.main_container.geometry()
            button_width = self.conversation_history_button.width()
            button_height = self.conversation_history_button.height()
            
            # x = container_geometry.width() - button_width - 2   # 2px from right edge
            x = 5
            y = (container_geometry.height() - button_height) // 2
            
            self.conversation_history_button.move(x, y)
            self.logger.debug(f"Conversation history button positioned at ({x}, {y})")
            
        except Exception as e:
            self.logger.error(f"Error positioning conversation history button: {e}")

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
    
    def on_input_changed(self, text):
        if  self.is_multiline_input():
            self.handle_multiline_resize()
        if text.strip():
            self.set_visual_state("typing")
        else:
            # Text does not exist
            self.set_visual_state("normal")
            self.hide_conversation_area()

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


    def handle_window_resize(self, window_size):
        """Handle window resize to reposition elements and adjust constraints."""
        if hasattr(self, 'conversation_toggle_button'):
            self.position_conversation_toggle_button()

        if hasattr(self, 'conversation_history_button') and self.conversation_history_button.isVisible():
            self.position_conversation_history_button()

        if (hasattr(self, 'conversation_history_widget') and self.conversation_history_widget and self.conversation_history_widget.isVisible()):
            self._position_history_widget()

        # Dynamically adjust response area constraints based on window size
        if hasattr(self, 'conversation_area'):
            window_height = window_size.height()
            # Reserve space for input area, margins, and some padding
            available_height = window_height - ElementSize.RESPONSE_MARGIN_BOTTOM
            available_height = max(
                available_height, ElementSize.RESPONSE_AVAILABLE_HEIGHT_MINIMUM)

            # Set dynamic min/max based on available space
            min_response_height = min(
                ElementSize.RESPONSE_MIN_HEIGHT, available_height * ElementSize.RESPONSE_MIN_HEIGHT_RATIO)
            max_response_height = max(
                available_height * ElementSize.RESPONSE_AVAILABLE_HEIGHT_MINIMUM, min_response_height)

            # Ensure both values are positive
            min_response_height = max(
                int(min_response_height), ElementSize.RESPONSE_MIN_ABSOLUTE_HEIGHT)
            max_response_height = max(
                int(max_response_height), min_response_height)

            self.conversation_widget.conversation_area.setMinimumHeight(min_response_height)
            self.conversation_widget.conversation_area.setMaximumHeight(max_response_height)

        # Reposition error message if it's visible
        if self.error_message and self.error_message.isVisible():
            self._position_error_message()

    def show_error_message(self, message):
        """Show error message in a floating popup for 5 seconds."""
        try:
            # Create error message widget if it doesn't exist
            if self.error_message is None:
                self.error_message = ErrorMessage(self.parent)
                self.error_message.setStyleSheet(self.style_manager.get_error_message_style())
            
            # Position the error message above the input field
            self._position_error_message()
            
            # Show the message
            self.error_message.show_message(message, 5000)
            
            self.logger.debug(f"Showing error message: {message}")
            
        except Exception as e:
            self.logger.error(f"Error showing error message: {e}")

    def _position_error_message(self):
        """Position the error message in the center of the current window's content area."""
        if not self.error_message or not self.parent:
            return
            
        try:
            # Get the actual content area (excluding window frame)
            content_rect = self.parent.centralWidget().geometry() if self.parent.centralWidget() else self.parent.rect()
            content_global_pos = self.parent.mapToGlobal(content_rect.topLeft())
            
            # Calculate error message size
            self.error_message.adjustSize()
            error_width = self.error_message.width()
            error_height = self.error_message.height()
            
            # Position in exact center of content area
            x = content_global_pos.x() + (content_rect.width() - error_width) // 2
            y = content_global_pos.y() + (content_rect.height() - error_height) // 2
            
            # Ensure it stays within screen bounds
            screen = self.parent.screen().geometry()
            x = max(10, min(x, screen.width() - error_width - 10))
            y = max(10, min(y, screen.height() - error_height - 10))
            
            self.error_message.move(x, y)
            
            self.logger.debug(f"Positioned error message at center ({x}, {y}) - content area: {content_rect.width()}x{content_rect.height()}")
            
        except Exception as e:
            self.logger.error(f"Error positioning error message: {e}")


    def clear_response_on_minimize(self):
        """Clear response area and contract UI when showing window"""
        try:
            # Clear the response area
            self.clear_conversation_area()
            self.logger.debug("Response area cleared")
            
            # Contract the UI if it's expanded
            if self.is_currently_expanded():
                self.hide_conversation_area()
                self.logger.debug("UI contracted after clearing response")
                
            # Clear state manager's accumulated response
            if hasattr(self, 'state_manager'):
                # self.state_manager.clear_accumulated_response()
                self.hide_conversation_area()
                self.logger.debug("State manager response cleared")
                
            # Reset input field focus
            self.input_field.setFocus()
                
        except Exception as e:
            self.logger.error(f"Error clearing response on show: {e}")

    def _create_conversation_history_widget(self):
        """Create the conversation history widget."""
        self.conversation_history_widget = ConversationHistoryWidget(
            style_manager=self.style_manager,
            parent=self.main_container
        )
        
        # Set conversation manager
        if self.conversation_manager:
            self.conversation_history_widget.set_conversation_manager(self.conversation_manager)
        
        # Connect signals
        self.conversation_history_widget.conversation_selected.connect(self._on_history_conversation_selected)
        self.conversation_history_widget.history_cleared.connect(self._on_history_cleared)
        self._hide_history_widget()

    def _on_history_conversation_selected(self, conversation_id: str):
        """Handle when a conversation is selected from history."""
        try:
            self.logger.debug(f"History conversation selected: {conversation_id}")

            self.conversation_widget.show_conversation_history(conversation_id)
        
            if not self.conversation_visible:
                self.show_conversation_area()
            
            self._hide_history_widget()
            self.input_field.setFocus()
            self.set_visual_state("normal")
            
        except Exception as e:
            self.logger.error(f"Error handling history conversation selection: {e}")
            self.show_error_message("Failed to load selected conversation")
            
        except Exception as e:
            self.logger.error(f"Error handling history conversation selection: {e}")
            self.show_error_message("Failed to load selected conversation")



    def _on_history_cleared(self):
        """Handle when conversation history is cleared."""
        try:
            self.logger.debug("Conversation history cleared")
            self._hide_history_widget()
            
            if self.is_showing_history():
                self.clear_conversation_area()       
            # TODO move to info message
            message = "Conversation history was cleared!"
            self.show_error_message(message)

        except Exception as e:
            self.logger.error(f"Error handling history cleared: {e}")



    def show_history_widget(self):
        """Show the conversation history widget."""
        try:
            if not hasattr(self, 'conversation_history_widget') or not self.conversation_history_widget:
                self.logger.warning("Conversation history widget not initialized")
                return
            
            self._position_history_widget()
            
            self.conversation_history_widget.setVisible(True)
            self.conversation_history_widget.raise_()
            self.conversation_history_widget.load_conversations()
            
            self.logger.debug("Conversation history widget shown")
            
        except Exception as e:
            self.logger.error(f"Error showing history widget: {e}")

    def _hide_history_widget(self):
        """Hide the conversation history widget."""
        try:
            if hasattr(self, 'conversation_history_widget') and self.conversation_history_widget:
                self.conversation_history_widget.setVisible(False)
                self.logger.debug("Conversation history widget hidden")
        except Exception as e:
            self.logger.error(f"Error hiding history widget: {e}")

    def toggle_history_widget(self):
        """Toggle the visibility of conversation history widget."""
        try:
            if (hasattr(self, 'conversation_history_widget') and 
                self.conversation_history_widget and 
                self.conversation_history_widget.isVisible()):
                self._hide_history_widget()
            else:
                self.show_history_widget()
            self.update_conversation_history_toggle_button()
        except Exception as e:
            self.logger.error(f"Error toggling history widget: {e}")


    def _position_history_widget(self):
        """Position the conversation history widget in the center of the main container."""
        try:
            if not self.conversation_history_widget or not self.main_container:
                return
            
            container_geom = self.main_container.geometry()
            
            widget_width = min(600, int(container_geom.width() * 0.8))
            widget_height = min(400, int(container_geom.height() * 0.8))
            
            x = (container_geom.width() - widget_width) // 2
            y = (container_geom.height() - widget_height) // 2
            
            self.conversation_history_widget.setGeometry(x, y, widget_width, widget_height)
            
            self.logger.debug(f"History widget positioned at ({x}, {y}) with size {widget_width}x{widget_height}")
            
        except Exception as e:
            self.logger.error(f"Error positioning history widget: {e}")



