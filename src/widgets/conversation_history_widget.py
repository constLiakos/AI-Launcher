import logging
from typing import Optional, List, Dict
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QFrame, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
from managers.style_manager import StyleManager
from utils.constants import ElementSize, Files


class ConversationHistoryWidget(QWidget):
    """Widget for displaying and managing conversation history."""
    
    # Signals
    conversation_selected = pyqtSignal(str)
    history_cleared = pyqtSignal()
    
    def __init__(self, style_manager: StyleManager, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.style_manager = style_manager
        self.conversation_manager = None
        
        # UI Components
        self.search_field = None
        self.history_list = None
        self.clear_button = None
        self.refresh_button = None
        self.status_label = None
        
        # Data
        self.conversations_data = []
        self.filtered_conversations = []
        
        self._setup_ui()
        self._apply_styles()
        
    def _setup_ui(self):
        """Setup the UI components."""
        # self.setFixedSize(350, 450)  # Adjust size as needed
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Conversation History")
        title_label.setObjectName("historyTitle")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon(str(Files.REFRESH_ICON_PATH)))
        self.refresh_button.setObjectName("historyRefreshButton")
        self.refresh_button.setFixedSize(24, 24)
        self.refresh_button.setToolTip("Refresh history")
        self.refresh_button.clicked.connect(self.refresh_history)
        header_layout.addWidget(self.refresh_button)
        
        # Clear button
        self.clear_button = QPushButton("🗑️")
        self.clear_button.setObjectName("historyClearButton")
        self.clear_button.setFixedSize(24, 24)
        self.clear_button.setToolTip("Clear all history")
        self.clear_button.clicked.connect(self._confirm_clear_history)
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # Search field
        self.search_field = QLineEdit()
        self.search_field.setObjectName("historySearchField")
        self.search_field.setPlaceholderText("Search conversations...")
        self.search_field.textChanged.connect(self._filter_conversations)
        layout.addWidget(self.search_field)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.itemClicked.connect(self._on_item_clicked)
        self.history_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.history_list)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("historyStatus")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
    def _apply_styles(self):
        """Apply styles to the widget."""
        self.setObjectName("conversation_history_widget")
        # Set attribute to ensure background is painted
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(self.style_manager.get_conversation_history_style())
        self.style().unpolish(self)
        self.style().polish(self)

    def reapply_styles(self):
        """Reapply Styles"""
        self._apply_styles()

    def set_conversation_manager(self, conversation_manager):
        """Set the conversation manager."""
        self.conversation_manager = conversation_manager
        self.refresh_history()
        
    def refresh_history(self):
        """Refresh the conversation history from the manager."""
        if not self.conversation_manager:
            self.logger.warning("No conversation manager set")
            self._show_status("No conversation manager available", is_error=True)
            return
            
        try:
            self.logger.debug("Refreshing conversation history")
            # Use the new method designed for the widget
            self.conversations_data = self.conversation_manager.get_conversation_history_for_widget(limit=50)
            self.filtered_conversations = self.conversations_data.copy()
            self._populate_history_list()
            
            if self.conversations_data:
                self._show_status(f"Loaded {len(self.conversations_data)} conversations")
            else:
                self._show_status("No conversations found")
                
        except Exception as e:
            self.logger.error(f"Error refreshing history: {e}")
            self._show_status("Error loading history", is_error=True)
            
    def _populate_history_list(self):
        """Populate the history list with conversations."""
        self.history_list.clear()
        
        if not self.filtered_conversations:
            item = QListWidgetItem("No conversations found")
            item.setData(Qt.UserRole, None)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Make non-selectable
            self.history_list.addItem(item)
            return
            
        for conversation in self.filtered_conversations:
            item = self._create_history_item(conversation)
            self.history_list.addItem(item)
            
    def _create_history_item(self, conversation: Dict) -> QListWidgetItem:
        """Create a list item for a conversation."""
        user_message = conversation.get('user_message', 'Unknown')
        timestamp = conversation.get('timestamp', '')
        
        # Create display text
        display_text = self._truncate_text(user_message, 60)
        
        if timestamp:
            # Format timestamp if it's a datetime string
            try:
                from datetime import datetime
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%m/%d %H:%M')
                else:
                    formatted_time = str(timestamp)
                display_text = f"{formatted_time} - {display_text}"
            except:
                display_text = f"{timestamp} - {display_text}"
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, conversation)
        item.setToolTip(self._create_tooltip(conversation))
        
        return item
        
    def _create_tooltip(self, conversation: Dict) -> str:
        """Create a tooltip for a conversation item."""
        user_message = conversation.get('user_message', 'Unknown')
        assistant_response = conversation.get('assistant_response', '')
        timestamp = conversation.get('timestamp', '')
        
        tooltip = f"User: {user_message}"
        if assistant_response:
            truncated_response = self._truncate_text(assistant_response, 200)
            tooltip += f"\n\nAssistant: {truncated_response}"
        if timestamp:
            tooltip += f"\n\nTime: {timestamp}"
            
        return tooltip
        
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to max_length with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
        
    def _filter_conversations(self, search_text: str):
        """Filter conversations based on search text."""
        if not search_text:
            self.filtered_conversations = self.conversations_data.copy()
        else:
            search_lower = search_text.lower()
            self.filtered_conversations = [
                conv for conv in self.conversations_data
                if search_lower in conv.get('user_message', '').lower() or
                   search_lower in conv.get('assistant_response', '').lower()
            ]
            
        self._populate_history_list()
        
        # Update status
        if search_text:
            self._show_status(f"Found {len(self.filtered_conversations)} matching conversations")
        else:
            self._show_status(f"Showing {len(self.conversations_data)} conversations")
            
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle single click on history item."""
        conversation_data = item.data(Qt.UserRole)
        if conversation_data:
            self.logger.debug("History item clicked")
            # Could add preview or selection highlighting here
            
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double click on history item."""
        conversation_data = item.data(Qt.UserRole)
        if conversation_data:
            # self.logger.debug("History item double-clicked, loading conversation")
            # self.conversation_selected.emit(conversation_data)
            conversation_id = conversation_data.get('conversation_id')
            if conversation_id:
                self.logger.debug(f"History item double-clicked, emitting conversation ID: {conversation_id}")
                self.conversation_selected.emit(conversation_id)
            else:
                self.logger.warning("No conversation ID found in conversation data")

    def _confirm_clear_history(self):
        """Confirm before clearing history."""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            'Clear History', 
            'Are you sure you want to clear all conversation history?\n\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._clear_history()
            
    def _clear_history(self):
        """Clear all conversation history."""
        try:
            if self.conversation_manager:
                # Use the new clear method
                if self.conversation_manager.clear_all_conversations():
                    self.refresh_history()
                    self.history_cleared.emit()
                    self._show_status("History cleared successfully")
                else:
                    self._show_status("Failed to clear history", is_error=True)
            else:
                self.logger.warning("No conversation manager available")
                self._show_status("No conversation manager available", is_error=True)
                
        except Exception as e:
            self.logger.error(f"Error clearing history: {e}")
            self._show_status("Error clearing history", is_error=True)
            
    def _show_status(self, message: str, is_error: bool = False):
        """Show status message."""
        self.status_label.setText(message)
        if is_error:
            self.status_label.setObjectName("historyStatusError")
        else:
            self.status_label.setObjectName("historyStatus")
        self.status_label.setStyle(self.status_label.style())
        
        # Clear status after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
        
    def get_selected_conversation(self) -> Optional[Dict]:
        """Get the currently selected conversation."""
        current_item = self.history_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
        
    def select_conversation_by_index(self, index: int):
        """Select a conversation by its index."""
        if 0 <= index < self.history_list.count():
            self.history_list.setCurrentRow(index)
            
    def get_conversation_count(self) -> int:
        """Get the total number of conversations."""
        return len(self.conversations_data)
    

