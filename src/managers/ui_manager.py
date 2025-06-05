import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
                             QPushButton, QTextBrowser, QFrame, QShortcut,
                             QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QKeySequence, QFontDatabase
from managers.conversation_manager import ConversationManager
from managers.style_manager import StyleManager
from utils.constants import (
    ElementSize, Files, InputSettings, Text, WindowSize)
from utils.markdown_render import MarkdownRenderer


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
        self.conversation_area = None
        self.stt_button = None
        self.settings_button = None
        self.copy_button = None
        self.history_button = None  # New button for conversation history
        self.input_type_is_multiline = False
        self.multiline_toggle_button = None
        self.conversation_toggle_button = None

        self.original_input_height = None
        self.original_window_height = None
        self.min_window_height = WindowSize.COMPACT_HEIGHT
        self.animation_callbacks = {}
        self.state_manager_callbacks = {}

        self.current_visual_state = "normal"
        self.is_expanded = False
        self.conversation_visible = False

        self.show_history_mode = False
        self.conversation_manager:ConversationManager = None
        self.markdown_render = MarkdownRenderer(logger)
        self.style_manager = StyleManager(logger)


    def setup_ui(self, multiline_input=False):
        """Create and setup all UI components."""
        self.input_type_is_multiline = multiline_input
        self._create_main_container()
        self._create_input_section()
        self._create_response_section()
        self._create_conversation_toggle_button()
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
        if 'start_thinking_animation' in callbacks:
            self.animation_callbacks['start_thinking'] = callbacks['start_thinking_animation']
        if 'stop_thinking_animation' in callbacks:
            self.animation_callbacks['stop_thinking'] = callbacks['stop_thinking_animation']

        self.multiline_toggle_button.clicked.connect(self._toggle_input_type)
        self.conversation_toggle_button.clicked.connect(self.toggle_response_visibility)
        self.history_button.clicked.connect(self._toggle_history_view)
        self.copy_button.clicked.connect(callbacks['copy_clicked'])

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
        """Expand UI to show conversation area - alias for show_conversation_area."""
        self.show_conversation_area()

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

            if hasattr(self.conversation_toggle_button, 'clicked'):  # Add this block
                try:
                    self.conversation_toggle_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.history_button, 'clicked'):
                try:
                    self.history_button.clicked.disconnect()
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

    def show_conversation_area(self):
        """Show response area and copy button."""
        if not self.conversation_visible:
            if self.is_multiline_input():
                self.handle_multiline_resize()
            
            self.response_container.setVisible(True)
            self.conversation_area.setVisible(True)
            self.conversation_visible = True
            self.is_expanded = True
            self.expansion_changed.emit(True)
            self.update_conversation_toggle_button(True)
            
            # Reposition the toggle button after expansion
            QTimer.singleShot(10, self.position_conversation_toggle_button)
            
            self.logger.debug("Response area shown")

    def hide_conversation_area(self):
        """Hide response area and copy button."""
        if self.conversation_visible:
            if self.is_multiline_input():
                self.handle_multiline_resize()
            self.copy_button.setVisible(False)
            self.conversation_visible = False
            self.is_expanded = False
            self.expansion_changed.emit(False)
            self.update_conversation_toggle_button(False)
            
            QTimer.singleShot(10, self.position_conversation_toggle_button)
            QTimer.singleShot(50, lambda: self.response_container.setVisible(False))
            self.logger.debug("Response area hidden")

    def set_conversation_manager(self, conversation_manager):
        """Set the conversation manager reference."""
        self.conversation_manager = conversation_manager

    def _toggle_history_view(self):
        """Toggle between showing last response only and full conversation history."""
        self.logger.debug("toggle history view button triggered")
        self.show_history_mode = not self.show_history_mode
        
        if self.show_history_mode:
            self._show_conversation_history()
            self.history_button.setIcon(QIcon(str(Files.CONVERSATION_BTN_SHOW_RESPONSE_PATH)))
        else:
            self.set_response_text(self.get_current_response_text())
            self.history_button.setIcon(QIcon(str(Files.CONVERSATION_BTN_SHOW_HISTORY_PATH)))

    def _show_conversation_history(self):
        """Display the full conversation history."""
        self.get_current_response_text()
        if not self.conversation_manager:
            self.logger.warning("No conversation manager available")
            return
        
        try:
            history = self.conversation_manager.get_conversation_history()
            if not history:
                self.conversation_area.setHtml("<p><i>No conversation history available.</i></p>")
                return
            
            html_content = self._format_conversation_history(history)
            self.conversation_area.setHtml(html_content)
            self._setup_emoji_font(self.conversation_area)
            
            # Scroll to the bottom to show most recent messages
            scrollbar = self.conversation_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            self.logger.error(f"Error loading conversation history: {e}")
            self.conversation_area.setHtml("<p><i>Error loading conversation history.</i></p>")
            self._setup_emoji_font(self.conversation_area)

    def _format_conversation_history(self, history):
        """Format conversation history as HTML for display with text message bubble style."""
        html_parts = self._build_html_header()
        
        for message in history:
            if formatted_message := self._format_single_message(message):
                html_parts.append(formatted_message)
        html_parts.append("</body></html>")
        return "".join(html_parts)

    def _build_html_header(self):
        """Build the HTML header with styles."""
        return [f"""
                <!DOCTYPE html><html><head><style>
                {self.style_manager.get_history_conversation_style()}
                </style></head><body>"""]

    def _format_single_message(self, message):
        """Format a single message into HTML."""
        role = message.get('role', 'unknown')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')
        
        # Skip empty messages
        if not content.strip():
            return None
        
        time_str = self._format_timestamp(timestamp)
        formatted_content = self.markdown_render.to_html(content) if content else ""
        
        # Message formatters mapping
        formatters = {
            'user': self._format_user_message,
            'assistant': self._format_assistant_message,
            'system': self._format_system_message
        }
        
        formatter = formatters.get(role)
        if formatter:
            return formatter(formatted_content, time_str)
        
        return None

    def _format_timestamp(self, timestamp):
        """Format timestamp string for display."""
        if not timestamp:
            return ""
        
        try:
            from datetime import datetime
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            return dt.strftime('%H:%M')
        except Exception:
            return str(timestamp)[:5] if timestamp else ""

    def _get_icon(self, icon_attr, fallback_emoji):
        """Get icon HTML or fallback emoji."""
        if hasattr(Files, icon_attr):
            icon_path = getattr(Files, icon_attr)
            return f"<img src='{str(icon_path)}' width='18' height='18' style='vertical-align: middle;'>"
        return fallback_emoji

    def _format_user_message(self, content, time_str):
        """Format user message HTML."""
        user_icon = self._get_icon('USER_ICON_PATH', "👤")
        return f"""
        <div class='message-container'>
            <div class='user-message-wrapper'>
                <div class='user-message'>
                    <div class='message-header-user'>
                        You {time_str} {user_icon}
                    </div>
                    <div class='message-content'>{content}</div>
                </div>
            </div>
        </div>
        """

    def _format_assistant_message(self, content, time_str):
        """Format assistant message HTML."""
        bot_icon = self._get_icon('ASSISTANT_ICON_PATH', "🤖")
        return f"""
        <div class='message-container'>
            <div class='assistant-message-wrapper'>
                <div class='assistant-message'>
                    <div class='message-header-assistant'>
                        {bot_icon} Assistant {time_str}
                    </div>
                    <div class='message-content'>{content}</div>
                </div>
            </div>
        </div>
        """

    def _format_system_message(self, content, time_str):
        """Format system message HTML."""
        system_icon = self._get_icon('SETTINGS_GEAR_ICON_PATH', "⚙️")
        if hasattr(Files, 'SETTINGS_GEAR_ICON_PATH'):
            system_icon = system_icon.replace('vertical-align: middle;', 'vertical-align: middle; margin-right: 4px;')
        
        time_html = f"<br><small>{time_str}</small>" if time_str else ""
        return f"""
        <div class='message-container'>
            <div class='system-message'>
                {system_icon}System: {content}
                {time_html}
            </div>
        </div>
        """

    def set_response_text(self, text):
        """Set response text - now aware of history mode."""
        self.show_history_mode = False
        self._current_response = text
        html_content = self.markdown_render.to_html(text)
        self.conversation_area.setHtml(html_content)

    def is_showing_history(self):
        """Check if currently showing conversation history."""
        return self.show_history_mode


    def append_response_text(self, text):
        """Append text to response - only works in current response mode."""
        if not self.show_history_mode:
            current = self.conversation_area.toHtml()
            self.conversation_area.setHtml(current + text)
            # self._current_response = self.conversation_area.toHtml()

    def get_current_response_text(self):
        """Get the current response text."""
        return getattr(self, '_current_response', '')

    def _escape_html(self, text):
        """Escape HTML characters in text content."""
        import html
        return html.escape(str(text)).replace('\n', '<br>')

    def is_conversation_visible(self):
        return self.conversation_visible

    def toggle_response_visibility(self):
        """Toggle response area visibility."""
        self.logger.debug(f"toggle_response_visibility, conversation is : {self.conversation_visible}")
        if self.conversation_visible:
            self.hide_conversation_area()
        else:
            self.show_conversation_area()


    def _create_response_section(self):
        """Create response area with history button."""
        container_layout = self.main_container.layout()

        # Create a container for the response section
        response_container = QWidget()
        response_layout = QVBoxLayout(response_container)
        response_layout.setContentsMargins(0, 0, 0, 0)
        response_layout.setSpacing(5)

        # Create horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        history_button = self._create_history_toggle_button()
        copy_button = self._create_copy_button()
        
        button_layout.addWidget(history_button, alignment=Qt.AlignLeft)
        button_layout.addStretch()  # This pushes buttons to opposite sides
        button_layout.addWidget(copy_button, alignment=Qt.AlignRight)
        
        response_layout.addLayout(button_layout)

        # Create conversation area
        self.conversation_area = QTextBrowser()
        self.conversation_area.setObjectName("conversationArea")
        self.conversation_area.setAcceptRichText(True)
        self.conversation_area.setOpenExternalLinks(True)
        self.conversation_area.setVisible(False)
        self.conversation_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._setup_emoji_font(self.conversation_area)
        response_layout.addWidget(self.conversation_area)

        # Store references
        self.response_container = response_container
        self.history_button_container = history_button  # Store for potential future use
        
        # Hide the response container initially
        response_container.setVisible(False)
        
        container_layout.addWidget(response_container)
        container_layout.setStretchFactor(container_layout.itemAt(0).layout(), 0)  # Input section
        container_layout.setStretchFactor(response_container, 1)  # Response area takes remaining space
        container_layout.addStretch()

#   ##########################################################################################
#       Button Functions
#   ##########################################################################################

    def position_conversation_toggle_button(self):
        """Position the conversation toggle button at the bottom edge of the window."""
        if not self.conversation_toggle_button or not self.main_container:
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


    def _create_copy_button(self):
        self.copy_button = QPushButton(Text.COPY_BUTTON)
        self.copy_button.setToolTip("Copy Button")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setFixedSize(ElementSize.COPY_BUTTON_WIDTH, ElementSize.COPY_BUTTON_HEIGHT)
        return self.copy_button

    def _create_conversation_toggle_button(self):
        """Create the conversation toggle button as a floating element at bottom edge."""
        self.conversation_toggle_button = QPushButton()
        self.conversation_toggle_button.setParent(self.main_container)
        self.conversation_toggle_button.setFixedSize(ElementSize.CONVERSATION_TOGGLE_BUTTON_WIDTH, ElementSize.CONVERSATION_TOGGLE_BUTTON_HEIGHT)
        self.conversation_toggle_button.setFont(QFont("Segoe UI", 8))
        self.update_conversation_toggle_button(self.conversation_visible)
        self.position_conversation_toggle_button()
        self.conversation_toggle_button.raise_()

    def _create_history_toggle_button(self):
        # Create history button container
        self.history_button = QPushButton()
        self.history_button.setIcon(QIcon(str(Files.CONVERSATION_BTN_SHOW_HISTORY_PATH)))  # Replace with your icon path
        self.history_button.setToolTip("Show Conversation History")
        self.history_button.setObjectName("historyButton")
        self.history_button.setFixedHeight(30)
        self.history_button.setFixedWidth(30)
    
        return self.history_button

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


    def handle_window_resize(self, window_size):
        """Handle window resize to reposition elements and adjust constraints."""
        if hasattr(self, 'conversation_toggle_button'):
            self.position_conversation_toggle_button()

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

            self.conversation_area.setMinimumHeight(min_response_height)
            self.conversation_area.setMaximumHeight(max_response_height)
