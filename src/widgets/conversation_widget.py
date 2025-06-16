import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QApplication,
                             QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from managers.conversation_manager import ConversationManager
from utils.constants import Files, ElementSize, Text, Timing
from utils.markdown_render import MarkdownRenderer

class ConversationWidget(QWidget):
    """Widget for handling conversation display and history management."""
    
    # Signals
    copy_requested = pyqtSignal()
    history_cleared = pyqtSignal()
    
    def __init__(self, style_manager, logger, parent=None):
        super().__init__(parent)
        self.style_manager = style_manager
        self.logger = logger.getChild('conversation_widget')
        self.conversation_manager = None
        self.markdown_render = MarkdownRenderer(logger, style_manager)
        
        # State
        self.show_history_mode = False
        self._current_response = ""
        
        # UI Components
        self.conversation_area = None
        self.history_button = None
        self.clear_history_button = None
        self.copy_button = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the conversation widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create button layout
        self._create_button_section(layout)
        
        # Create conversation area
        self._create_conversation_area(layout)
    
    def _create_button_section(self, parent_layout):
        """Create the button section."""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # History toggle button
        self.history_button = QPushButton()
        self.history_button.setIcon(QIcon(str(Files.CONVERSATION_BTN_SHOW_HISTORY_PATH)))
        self.history_button.setToolTip("Show Conversation History")
        self.history_button.setObjectName("historyButton")
        self.history_button.setFixedSize(30, 30)
        
        # Clear history button
        self.clear_history_button = QPushButton()
        self.clear_history_button.setIcon(QIcon(str(Files.CLEAR_CONVESRATION_BTN)))
        self.clear_history_button.setToolTip("Clear Conversation History")
        self.clear_history_button.setObjectName("clearHistoryButton")
        self.clear_history_button.setFixedSize(30, 30)
        
        # Copy button
        self.copy_button = QPushButton(Text.COPY_BUTTON)
        self.copy_button.setToolTip("Copy Response")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setFixedSize(ElementSize.COPY_BUTTON_WIDTH, ElementSize.COPY_BUTTON_HEIGHT)
        
        # Layout buttons
        button_layout.addWidget(self.history_button, alignment=Qt.AlignLeft)
        button_layout.addWidget(self.clear_history_button, alignment=Qt.AlignLeft)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_button, alignment=Qt.AlignRight)
        
        parent_layout.addLayout(button_layout)
    
    def _create_conversation_area(self, parent_layout):
        """Create the conversation display area."""
        self.conversation_area = QTextBrowser()
        self.conversation_area.setObjectName("conversationArea")
        self.conversation_area.setAcceptRichText(True)
        self.conversation_area.setOpenExternalLinks(True)
        self.conversation_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._setup_emoji_font(self.conversation_area)
        
        parent_layout.addWidget(self.conversation_area)
    

    def _disconnect_all_signals(self):
        """Disconnect all signals before reconnecting"""
        try:

            if hasattr(self.copy_button, 'clicked'):
                try:
                    self.copy_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.history_button, 'clicked'):
                try:
                    self.history_button.clicked.disconnect()
                except TypeError:
                    pass

            if hasattr(self.clear_history_button, 'clicked'):
                try:
                    self.clear_history_button.clicked.disconnect()
                except TypeError:
                    pass

        except Exception as e:
            self.logger.error(f"Error disconnecting signals: {e}")

    def _connect_signals(self):
        """Connect internal signals."""
        self._disconnect_all_signals()
        self.history_button.clicked.connect(self._toggle_history_view)
        self.clear_history_button.clicked.connect(self._clear_history)
        self.copy_button.clicked.connect(self.copy_request)
    
    def set_conversation_manager(self, conversation_manager:ConversationManager):
        """Set the conversation manager reference."""
        self.conversation_manager = conversation_manager
    
    def set_response_text(self, text):
        """Set response text - aware of history mode."""
        self._current_response = text
        
        if self.show_history_mode:
            self._show_conversation_history()
        else:
            html_content = self.markdown_render.to_html(text)
            self.conversation_area.setHtml(html_content)

    def copy_request(self):
        self.logger.debug("Copy Request")
        self.copy_requested.emit()

        try:
            response_text = self._current_response   #self.state_manager.accumulated_response or self.get_coversation_area_text()
            if response_text.strip():
                clipboard = QApplication.clipboard()
                clipboard.setText(response_text)

                # Visual feedback
                original_text = self.copy_button.text()
                self.copy_button.setText(Text.COPY_SUCCESS)
                self.copy_button.setStyleSheet(
                    self.style_manager.button_styles.get_copy_button_success_style())

                QTimer.singleShot(Timing.COPY_FEEDBACK_DURATION, lambda: (
                    self.copy_button.setText(original_text),
                    self.copy_button.setStyleSheet("")
                ))
        except Exception as e:
            self.logger.error(f"{Text.ERROR_COPYING_CLIPBOARD} {str(e)}")
    
    def append_response_text(self, text):
        """Append text to response - only works in current response mode."""
        if not self.show_history_mode:
            current = self.conversation_area.toHtml()
            self.conversation_area.setHtml(current + text)
    
    def get_current_response_text(self):
        """Get the current response text."""
        return self._current_response
    
    def is_showing_history(self):
        """Check if currently showing conversation history."""
        return self.show_history_mode
    
    def reapply_conversation_history_theme(self):
        """Reapply theme to conversation history."""
        if self.show_history_mode:
            self._show_conversation_history()
    
    def _toggle_history_view(self):
        """Toggle between showing last response only and full conversation history."""
        self.logger.debug("Toggle history view button triggered")
        self.show_history_mode = not self.show_history_mode
        
        self.set_response_text(self.get_current_response_text())
        
        if self.show_history_mode:
            self.history_button.setIcon(QIcon(str(Files.CONVERSATION_BTN_SHOW_RESPONSE_PATH)))
            self.history_button.setToolTip("Show Last Response Only")
        else:
            self.history_button.setIcon(QIcon(str(Files.CONVERSATION_BTN_SHOW_HISTORY_PATH)))
            self.history_button.setToolTip("Show Conversation History")
    
    def _clear_history(self):
        """Clear conversation history."""
        if self.conversation_manager:
            self.conversation_manager.clear_current_conversation()
            self.reapply_conversation_history_theme()
            self.history_cleared.emit()
    
    def _show_conversation_history(self):
        """Display the full conversation history."""
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
        """Format conversation history as HTML for display."""
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
                </style></head><body class='body'>"""]
    
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
            return f"<img src='{str(icon_path)}' width='25' height='25' style='vertical-align: middle;'>"
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



    def auto_scroll(self):
        cursor = self.conversation_area.textCursor()
        cursor.movePosition(cursor.End)
        self.conversation_area.setTextCursor(cursor)