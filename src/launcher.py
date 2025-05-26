# Add missing imports at the top
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QTextEdit, QFrame,
                             QApplication, QAction, QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu, QAction, QShortcut, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QKeySequence

from config import Config
from api_client import ApiClient
from managers.conversation_manager import ConversationManager
from settings_dialog import SettingsDialog
from managers.animation_manager import AnimationManager
from managers.styles import StyleManager
from managers.hotkey_manager import HotkeyManager
from utils.constants import Conversation, ElementSize, Style, Theme, WindowSize, Colors, Text, Timing, TrayIcon
from utils.markdown_render import MarkdownRenderer
from managers.state_manager import StateManager

logger = logging.getLogger(__name__)

class Launcher(QMainWindow):
    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug

        log_level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_launcher.log'),
                logging.StreamHandler()  # Still shows in console
            ]
        )
        
        # Initialize configuration
        self.config = Config()

        # Initialize API client
        self.api_client = ApiClient(self.config)

        # Initialize managers
        # Check if we should clear previous response when reopening
        convrestation_history_limit =  self.config.get('message_history_limit', Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT)

        self.conversation_manager = ConversationManager(logger, max_conversations=convrestation_history_limit)
        self.style_manager = StyleManager(logger)
        self.animation_manager = AnimationManager(self, logger, self.style_manager)
        self.state_manager = StateManager(self.config, logger)
        self.markdown_render = MarkdownRenderer(logger)
        self.hotkey_manager = HotkeyManager(logger, self.show_window, self.config)


        # Set current theme
        self.current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        self.style_manager.set_theme(self.current_theme)

        # Connect StateManager signals
        self.state_manager.state_changed.connect(self.on_state_changed)
        self.state_manager.processing_changed.connect(
            self.on_processing_changed)
        self.state_manager.response_ready.connect(self.on_response_ready)
        self.state_manager.request_cancelled.connect(self.on_request_cancelled)
        self.state_manager.request_ready.connect(self.send_request)
        self.state_manager.expanded_changed.connect(
            self.on_expanded_changed)  # New connection

        # Add a timer to debounce position saving (prevent excessive saves during dragging)
        self.position_save_timer = QTimer()
        self.position_save_timer.setSingleShot(True)
        self.position_save_timer.timeout.connect(self.save_geometry)

        # UI setup
        self.setup_ui()
        self.apply_modern_style()

        # Restore window position
        self.restore_geometry()

        # Setup system tray
        self.setup_system_tray()

        # Flag to track if app should really quit
        self.should_quit = False

        # Setup global hotkey
        self.hotkey_manager.setup_hotkey()

        self.resize_direction = None
        self.resize_start_pos = None
        self.resize_start_geometry = None

    def get_resize_direction(self, pos):
        """Determine resize direction based on mouse position."""
        rect = self.rect()

        left = pos.x() <= ElementSize.TRIGGER_EDGE_RESIZE_MARGIN_HORIZONTAL
        right = pos.x() >= rect.width() - ElementSize.TRIGGER_EDGE_RESIZE_MARGIN_HORIZONTAL
        top = pos.y() <= 0
        bottom = pos.y() >= rect.height() - ElementSize.TRIGGER_EDGE_RESIZE_MARGIN_VERTICAL
        
        if top and left:
            return "top-left"
        elif top and right:
            return "top-right"
        elif bottom and left:
            return "bottom-left"
        elif bottom and right:
            return "bottom-right"
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"
        else:
            return None


    def update_cursor(self, direction):
        """Update cursor based on resize direction."""
        if direction == "top-left" or direction == "bottom-right":
            self.setCursor(Qt.SizeFDiagCursor)
        elif direction == "top-right" or direction == "bottom-left":
            self.setCursor(Qt.SizeBDiagCursor)
        elif direction == "left" or direction == "right":
            self.setCursor(Qt.SizeHorCursor)
        elif direction == "top" or direction == "bottom":
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    # Remove the old hotkey methods and replace with:
    def restart_hotkey_listener(self):
        """Restart the global hotkey listener with new settings."""
        self.hotkey_manager.restart_listener()

    def quit_application(self):
        """Properly quit the application."""
        self.should_quit = True
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        QApplication.quit()

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

    def show_window(self):
        """Show and raise the window to front."""
        try:
            # Check if we should clear previous response when reopening
            if self.config.get('clear_previous_response', False):
                logger.debug("Clearing previous response on window show")
                # Clear the response area and hide it
                self.response_area.setText("")
                self.response_area.setVisible(False)
                self.copy_button.setVisible(False)
                # Reset to compact size
                self.animate_resize(WindowSize.COMPACT_WIDTH,
                                    WindowSize.COMPACT_HEIGHT, fast=True)
                # Clear the state manager's accumulated response
                if hasattr(self.state_manager, 'accumulated_response'):
                    self.state_manager.accumulated_response = ""
                # Clear input field
                self.input_field.clear()

                # Optionally clear conversation history when window reopens
                self.conversation_manager.clear_history()

            logger.debug(f"Window shown, position: ({self.x()}, {self.y()})")
            # First, ensure the window is visible
            if self.isMinimized():
                self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
            self.show()
            self.raise_()
            self.activateWindow()

            # Focus on the input field
            self.input_field.setFocus()
        except Exception as e:
            print(f"Error showing window: {e}")
            # Fallback - just show normally
            self.show()
            self.input_field.setFocus()

    def hide_window(self):
        """Hide the window to system tray."""
        self.hide()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                Text.TRAY_BACKGROUND_TITLE,
                Text.TRAY_BACKGROUND_MESSAGE,
                QSystemTrayIcon.Information,
                Timing.TRAY_MESSAGE_DURATION
            )

    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

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

    def setup_ui(self):
    # Remove window frame and title bar
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set initial size and allow resizing
        self.resize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)
        self.setMinimumSize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)  # Set reasonable minimums

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Main container with rounded corners
        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")

        # Main layout
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(ElementSize.CONTAINER_MARGIN_HORIZONTAL, ElementSize.CONTAINER_MARGIN_VERTICAL,
                                            ElementSize.CONTAINER_MARGIN_HORIZONTAL, ElementSize.CONTAINER_MARGIN_VERTICAL)
        container_layout.setSpacing(ElementSize.CONTAINER_SPACING)

        # Input section (this will stay fixed at the top)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(ElementSize.CONTAINER_SPACING)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("inputField")
        self.input_field.setPlaceholderText(Text.INPUT_PLACEHOLDER)
        self.input_field.textChanged.connect(self.on_input_changed)
        self.input_field.returnPressed.connect(self.force_send_request)
        input_layout.addWidget(self.input_field)

        # Settings button (gear icon)
        self.settings_button = QPushButton(Text.SETTINGS_BUTTON)
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setFixedSize(
            ElementSize.SETTINGS_BUTTON_SIZE, ElementSize.SETTINGS_BUTTON_SIZE)
        self.settings_button.clicked.connect(self.open_settings)
        input_layout.addWidget(self.settings_button)

        # Add input section to top of container (fixed position)
        container_layout.addLayout(input_layout)

        # Response area (appears below input, initially hidden)
        self.response_area = QTextEdit()
        self.response_area.setObjectName("responseArea")
        self.response_area.setReadOnly(True)
        self.response_area.setVisible(False)
        # self.response_area.setMinimumHeight(ElementSize.RESPONSE_MIN_HEIGHT)
        # self.response_area.setMaximumHeight(ElementSize.RESPONSE_MAX_HEIGHT)

        self.response_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container_layout.addWidget(self.response_area)

        # Set stretch factors - higher number gets more space (fix small response area)
        container_layout.setStretchFactor(self.input_field, 0)  # Fixed size
        container_layout.setStretchFactor(self.response_area, 1)  # Takes remaining space

        # Copy button positioned absolutely - make it a child of main_container instead
        self.copy_button = QPushButton(Text.COPY_BUTTON)
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setFixedSize(
            ElementSize.COPY_BUTTON_WIDTH, ElementSize.COPY_BUTTON_HEIGHT)
        self.copy_button.clicked.connect(self.copy_response)
        self.copy_button.setVisible(False)  # Hidden initially
        
        # Make it a child of main_container instead of response_area
        self.copy_button.setParent(self.main_container)
        
        # Ensure it's on top
        self.copy_button.raise_()

        # Add a stretch to push everything to the top if needed
        container_layout.addStretch()

        # Set central widget
        main_layout.addWidget(self.main_container)

        # Setup keyboard shortcuts
        self.setup_shortcuts()

    def set_input_state(self, state):
        """Set visual state of input field: 'normal', 'thinking' """
        if state == "typing":
            self.animation_manager.stop_thinking_animation()
            self.input_field.setObjectName("inputFieldTyping")
        elif state == "thinking":
            self.input_field.setObjectName("inputFieldThinking")
            self.animation_manager.start_thinking_animation(self.input_field)
        elif state == "streaming":
            self.animation_manager.stop_thinking_animation()
            self.input_field.setObjectName("inputFieldStreaming")
        else:  # normal
            self.animation_manager.stop_thinking_animation()
            self.input_field.setObjectName("inputField")

        # Reapply stylesheet to update appearance
        self.input_field.setStyle(self.input_field.style())


    def position_copy_button(self):
        """Position the copy button in the top-right corner of the response area, accounting for scrollbar."""
        if self.response_area.isVisible():
            # Get the response area's position relative to main_container
            response_pos = self.response_area.pos()
            response_geometry = self.response_area.geometry()
            
            # Calculate position relative to main_container
            button_x = response_pos.x() + response_geometry.width() - self.copy_button.width() - ElementSize.SCROLLBAR_SIZE - ElementSize.COPY_BUTTON_RIGHT_MARGIN
            button_y = response_pos.y() + ElementSize.COPY_BUTTON_RIGHT_MARGIN
            
            self.copy_button.move(button_x, button_y)
            self.copy_button.raise_()  # Bring to front
            
            # Ensure it stays visible
            self.copy_button.setVisible(True)

    def resizeEvent(self, event):
        """Handle window resize to reposition copy button and adjust response area."""
        super().resizeEvent(event)
        
        # Reposition copy button
        if hasattr(self, 'copy_button') and self.copy_button.isVisible():
            self.position_copy_button()
        
        # Dynamically adjust response area constraints based on window size
        if hasattr(self, 'response_area'):
            window_height = self.height()
            # Reserve space for input area, margins, and some padding
            available_height = window_height - 100  # Adjust this value as needed
            
            # Set dynamic min/max based on available space
            min_response_height = min(ElementSize.RESPONSE_MIN_HEIGHT, available_height * 0.3)
            max_response_height = max(available_height * 0.9, min_response_height)
            
            self.response_area.setMinimumHeight(int(min_response_height))
            self.response_area.setMaximumHeight(int(max_response_height))

    def hide_response(self):
        """Hide response using StateManager."""
        self.state_manager.hide_response()
        self.animate_resize(WindowSize.COMPACT_WIDTH,
                            WindowSize.COMPACT_HEIGHT, fast=True)
        QTimer.singleShot(50, lambda: self.response_area.setVisible(False))

    def copy_response(self):
        """Copy accumulated response text to clipboard."""
        try:
            response_text = self.state_manager.accumulated_response or self.response_area.toPlainText()
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
            else:
                self.show_status(Text.STATUS_NO_TEXT_TO_COPY)

        except Exception as e:
            print(f"{Text.ERROR_COPYING_CLIPBOARD} {str(e)}")
            self.show_status(Text.STATUS_COPY_FAILED)

    def animate_resize(self, width, height, fast=False):
        """Animate window resize using AnimationManager with constants."""
        # self.animation_manager.animate_resize(self, width, height, fast)
        self.animation_manager.animate_window_resize(self, width, height, fast)

    def apply_modern_style(self):
        """Apply the modern stylesheet using StyleManager."""
        self.setStyleSheet(self.style_manager.get_complete_style(self.current_theme))

    def _cleanup_worker(self):
        """Cleanup worker thread safely."""
        if self.state_manager.streaming_worker:
            if self.state_manager.streaming_worker.isRunning():
                self.state_manager.streaming_worker.terminate()
            self.state_manager.streaming_worker = None

    def cancel_current_request(self):
        """Improved cancellation with proper cleanup."""
        if not self.state_manager.is_processing:
            return
        # Increment request ID to invalidate current request
        self.state_manager.current_request_id += 1
        self.state_manager.is_processing = False
        # Stop and cleanup streaming worker
        if self.state_manager.streaming_worker and self.state_manager.streaming_worker.isRunning():
            self.state_manager.streaming_worker.stop()
            # Don't wait too long - use non-blocking approach
            QTimer.singleShot(Timing.WINDOW_FLAG_DELAY, self._cleanup_worker)
        # Cancel API request
        if hasattr(self.api_client, 'cancel_request'):
            try:
                self.api_client.cancel_request()
            except Exception as e:
                print(f"Error cancelling API request: {e}")
        # Re-enable UI immediately
        self.settings_button.setEnabled(True)

    def setup_shortcuts(self):
        # ESC to hide to tray
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.hide_window)

        # Ctrl+Q to quit completely
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.quit_application)

        # Ctrl+S for settings
        settings_action = QAction("Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+S"))
        settings_action.triggered.connect(self.open_settings)
        self.addAction(settings_action)

    @pyqtSlot(str)
    def send_request(self, prompt):
        """Send request - called by StateManager signal."""
        logger.debug(f"Sending request with prompt length: {len(prompt)}")
        if not prompt or self.state_manager.is_currently_processing():
            logger.debug("Request blocked - empty prompt or already processing")
            return

        # Store the current prompt for this conversation
        self.current_user_prompt = prompt

        # Start processing through StateManager
        request_id = self.state_manager.start_processing()
        logger.debug(f"Started processing with request_id: {request_id}")

        # Execute request
        QTimer.singleShot(50, lambda: self._execute_request(request_id))

    def _update_response_display(self):
        """Update response display with basic markdown formatting."""
        response_text = self.state_manager.get_accumulated_response()

        # Convert basic markdown to HTML
        html_content = self.markdown_render._basic_markdown_to_html(
            response_text)
        self.response_area.setHtml(html_content)

    def _handle_chunk(self, chunk, request_id):
        """Handle incoming response chunks with validation."""
        logger.debug(f"Received chunk for request {request_id}, size: {len(chunk)}")
        if not self.state_manager.is_request_valid(request_id):
            logger.debug(f"Invalid request_id {request_id}, ignoring chunk")
            return

        try:
            # Check if this is the first chunk and handle UI expansion
            self.state_manager.handle_first_chunk()

            # Add chunk to accumulated response
            self.state_manager.add_response_chunk(chunk)
            self._update_response_display()

            # Auto-scroll to bottom to show latest content
            cursor = self.response_area.textCursor()
            cursor.movePosition(cursor.End)
            self.response_area.setTextCursor(cursor)

        except Exception as e:
            print(f"Error handling chunk: {e}")
            self._handle_error(
                f"Error processing response: {str(e)}", request_id)

        except Exception as e:
            print(f"Error handling chunk: {e}")
            self._handle_error(
                f"Error processing response: {str(e)}", request_id)

    def _handle_completion(self, request_id):
        """Handle request completion with conversation storage."""
        if not self.state_manager.handle_completion(request_id):
            return

        # Get the complete response
        full_response = self.state_manager.get_accumulated_response()
        
        # Store the conversation (user prompt + assistant response)
        if hasattr(self, 'current_user_prompt') and full_response:
            self.conversation_manager.add_conversation(
                self.current_user_prompt, 
                full_response
            )
            logger.debug("Conversation added to history")

        # Final update of response
        self._update_response_display()

        # Return UI to normal state
        self.set_input_state("normal")
        self.settings_button.setEnabled(True)
        self.input_field.setFocus()

    def _handle_error(self, error_message, request_id):
        """Handle errors with validation."""
        logger.error(f"Request {request_id} failed: {error_message}")
        if not self.state_manager.handle_error(error_message, request_id):
            return
        
        # Get error text from StateManager
        error_text = self.state_manager.get_accumulated_response()

        # Update UI - expand if not visible
        if not self.response_area.isVisible():
            self.response_area.setVisible(True)
            self.copy_button.setVisible(True)
            self.position_copy_button()
            self.animate_resize(WindowSize.EXPANDED_WIDTH,
                                WindowSize.EXPANDED_HEIGHT)

        # Display error
        self.response_area.setText(error_text)

        # Return UI to normal state
        self.set_input_state("normal")
        self.settings_button.setEnabled(True)
        self.input_field.setFocus()

        # Clean up worker through StateManager
        self.state_manager.cleanup_worker_safely()

    def _execute_request(self, request_id):
        """Execute request using StateManager's worker creation."""
        try:
            # Get conversation history for context
            conversation_history = self.conversation_manager.get_conversation_history()

            worker = self.state_manager.create_streaming_worker(
                self.api_client, request_id, conversation_history)
            if not worker:
                return

            # Connect signals - FIXED: Use consistent method names
            worker.chunk_received.connect(
                lambda chunk: self._handle_chunk(chunk, request_id)
            )
            worker.response_complete.connect(
                lambda: self._handle_completion(request_id)
            )
            worker.error_occurred.connect(
                lambda error: self._handle_error(error, request_id)
            )

            worker.start()

        except Exception as e:
            self._handle_error(str(e), request_id)

    @pyqtSlot()
    def on_response_complete(self):
        """Handle response completion."""
        self.state_manager.is_processing = False
        self.show_status(Text.STATUS_COMPLETE)

        # Re-enable settings button
        self.settings_button.setEnabled(True)
        self.input_field.setFocus()

        # Hide status after a moment
        QTimer.singleShot(Timing.STATUS_HIDE_DELAY, self.hide_status)

    @pyqtSlot(bool)
    def on_expanded_changed(self, is_expanded):
        """Handle expansion state changes from StateManager."""
        if is_expanded:
            self.animate_resize(WindowSize.EXPANDED_WIDTH,
                                WindowSize.EXPANDED_HEIGHT)
            self.response_area.setVisible(True)
            self.copy_button.setVisible(True)
            self.position_copy_button()
        else:
            self.animate_resize(WindowSize.COMPACT_WIDTH,
                                WindowSize.COMPACT_HEIGHT)
            QTimer.singleShot(50, lambda: (
                self.response_area.setVisible(False),
                self.copy_button.setVisible(False)
            ))

    def show_status(self, message):
        """Print status instead of showing in UI."""
        # print(f"Status: {message}")
        pass

    def hide_status(self):
        """No-op since we don't have a status label."""
        pass

    def on_theme_changed(self, new_theme):
        """Handle theme change signal from settings dialog."""
        self.current_theme = new_theme
        self.style_manager.set_theme(new_theme)
        self.apply_modern_style()

    def open_settings(self):
        """Open the settings dialog."""
        logger.debug("Opening settings dialog")
        dialog:SettingsDialog = SettingsDialog(logger, self.config, self)

        # Connect the theme change signal
        dialog.theme_changed.connect(self.on_theme_changed)

        # Center the dialog relative to the main window
        main_rect = self.geometry()
        dialog_rect = dialog.geometry()
        center_x = main_rect.x() + (main_rect.width() - dialog_rect.width()) // 2
        center_y = main_rect.y() + (main_rect.height() - dialog_rect.height()) // 2
        dialog.move(center_x, center_y)

        if dialog.exec_():
            logger.debug(f"Settings saved, new theme: {new_theme}")
            # Check if theme changed
            new_theme = self.config.get('theme', Theme.DEFAULT_THEME)
            if new_theme != self.current_theme:
                self.current_theme = new_theme
                self.style_manager.set_theme(self.current_theme)

                self.apply_modern_style()
            # Show feedback with larger, visible status
            delay_seconds = self.config.get(
                'request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS)
            status_msg = f"✓ Settings saved! Request delay: {delay_seconds}s"
            self.show_status(status_msg)

            # Update API client
            self.api_client = ApiClient(self.config)
            self.restart_hotkey_listener()

            # Hide status after longer delay
            QTimer.singleShot(
                Timing.SETTINGS_FEEDBACK_DURATION, self.hide_status)

    def restore_geometry(self):
        """Restore window position (top-left corner)."""
        x = self.config.get('position_x', WindowSize.DEFAULT_X)
        y = self.config.get('position_y', WindowSize.DEFAULT_Y)
        logger.debug(f"Restoring window position to ({x}, {y})")
        self.move(x, y)

    def save_geometry(self):
        """Save window position (top-left corner)."""
        self.config.set('position_x', self.x())
        self.config.set('position_y', self.y())
        # Optional: for debugging
        logger.debug(f"Position saved: ({self.x()}, {self.y()})")

    def closeEvent(self, event):
        """Override close event to hide to tray instead of quitting."""
        logger.debug("Close event triggered")
        
        if not self.should_quit and hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            logger.debug("Hiding to tray instead of quitting")
            event.ignore()
            self.hide_window()
        else:
            logger.debug(f"Actually quitting - should_quit: {self.should_quit}, "
                        f"has_tray: {hasattr(self, 'tray_icon')}, "
                        f"tray_visible: {self.tray_icon.isVisible() if hasattr(self, 'tray_icon') else 'N/A'}")
            self.hotkey_manager.cleanup()
            logger.debug("Hotkey manager cleaned up")
            event.accept()
            logger.debug("Application closing")

    def mousePressEvent(self, event):
        """Enable window dragging and resizing."""
        if event.button() == Qt.LeftButton:
            self.resize_direction = self.get_resize_direction(event.pos())
            
            if self.resize_direction:
                # Starting resize
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
            else:
                # Starting drag
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle window dragging and resizing."""
        if event.buttons() == Qt.LeftButton:
            if self.resize_direction and hasattr(self, 'resize_start_pos'):
                # Handle resizing
                self.handle_resize(event.globalPos())
            elif hasattr(self, 'drag_position'):
                # Handle dragging
                self.move(event.globalPos() - self.drag_position)
                self.position_save_timer.stop()
                self.position_save_timer.start(500)
            
            event.accept()
        else:
            # Update cursor when hovering (not dragging)
            direction = self.get_resize_direction(event.pos())
            self.update_cursor(direction)


    def handle_resize(self, global_pos):
        """Handle window resizing based on direction."""
        if not self.resize_start_pos or not self.resize_start_geometry:
            return
        
        delta = global_pos - self.resize_start_pos
        start_geo = self.resize_start_geometry
        
        new_x = start_geo.x()
        new_y = start_geo.y()
        new_width = start_geo.width()
        new_height = start_geo.height()
        
        # Apply minimum size constraints
        min_size = self.minimumSize()
        
        if "left" in self.resize_direction:
            new_width = max(min_size.width(), start_geo.width() - delta.x())
            new_x = start_geo.x() + start_geo.width() - new_width
        elif "right" in self.resize_direction:
            new_width = max(min_size.width(), start_geo.width() + delta.x())
        
        if "top" in self.resize_direction:
            new_height = max(min_size.height(), start_geo.height() - delta.y())
            new_y = start_geo.y() + start_geo.height() - new_height
        elif "bottom" in self.resize_direction:
            new_height = max(min_size.height(), start_geo.height() + delta.y())
        
        # Apply the new geometry
        self.setGeometry(new_x, new_y, new_width, new_height)
        
        # Reposition copy button if visible
        if hasattr(self, 'copy_button') and self.copy_button.isVisible():
            self.position_copy_button()

    def leaveEvent(self, event):
        """Reset cursor when mouse leaves window."""
        if not self.resize_direction:  # Only reset if not currently resizing
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        """Clean up after mouse release."""
        if event.button() == Qt.LeftButton:
            self.resize_direction = None
            self.resize_start_pos = None
            self.resize_start_geometry = None
            self.setCursor(Qt.ArrowCursor)
            event.accept()

    def moveEvent(self, event):
        """Handle any window move event (including programmatic moves)."""
        super().moveEvent(event)

        # Debounce position saving for any move event
        if hasattr(self, 'position_save_timer'):
            self.position_save_timer.stop()
            self.position_save_timer.start(500)

    def on_state_changed(self, new_state):
        """Handle state changes from StateManager."""
        logger.debug(f"State changed to: {new_state}")
        self.set_input_state(new_state)
        
        if new_state == "normal" and not self.state_manager.get_current_prompt():
            logger.debug("State is normal with no prompt - checking if response should be hidden")
            if self.response_area.isVisible():
                logger.debug("Hiding response area")
                self.hide_response()

    def on_processing_changed(self, is_processing):
        """Handle processing state changes."""
        logger.debug(f"Processing state changed: {'started' if is_processing else 'stopped'}")
        self.settings_button.setEnabled(not is_processing)

    def on_response_ready(self, response):
        """Handle when response is ready to display."""
        logger.debug(f"Response ready, length: {len(response)} characters")
        self.response_area.setText(response)

    def on_request_cancelled(self):
        """Handle request cancellation."""
        logger.debug("Request cancelled - resetting UI state")
        self.set_input_state("normal")
        self.settings_button.setEnabled(True)

    def on_input_changed(self, text):
        """Simplified input handling - delegate to StateManager."""
        logger.debug(f"Input changed, length: {len(text)} characters")
        self.state_manager.set_prompt(text)

    def force_send_request(self):
        """Delegate to StateManager."""
        logger.debug("Force send request triggered (Enter key pressed)")
        self.state_manager.force_send_request()