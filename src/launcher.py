# Add missing imports at the top
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QAction, QShortcut)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence

from managers.recording_manager import Recording_Manager
from managers.tray_manager import TrayManager
from managers.ui_manager import UIManager
from managers.window_manager import WindowManager
from utils.config import Config
from utils.api_client import ApiClient
from managers.conversation_manager import ConversationManager
from utils.settings_dialog import SettingsDialog
from managers.animation_manager import AnimationManager
from managers.style_manager import StyleManager
from managers.hotkey_manager import HotkeyManager
from utils.constants import STT, Conversation, ElementSize, Files, InputSettings, Theme, WindowSize, Text, Timing
from utils.markdown_render import MarkdownRenderer
from managers.state_manager import StateManager
from utils.stt_api_client import SttApiClient

logger = logging.getLogger(__name__)


class Launcher(QMainWindow):
    def __init__(self, logdir: str, debug=False):
        super().__init__()

        self._setup_logging(logdir, debug)
        self._initialize_core_components()
        self._initialize_managers()
        self._setup_signal_connections()
        self.current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        self.style_manager.set_theme(self.current_theme)
        self.setup_ui()
        self.stt_configure()
        self.update_stt_button_visibility()
        self.apply_modern_style()
        self.window_manager.restore_geometry()
        self.tray_manager.setup_system_tray()
        # Flag to track if app should really quit
        self.should_quit = False
        self.hotkey_manager.setup_hotkey()
        self.hotkey_manager.hotkey_pressed.connect(self.show_window)
        self.hotkey_manager.stt_hotkey_pressed.connect(self._on_stt_hotkey_pressed)

    def _setup_logging(self, logdir, debug):
        """Setup logging configuration."""
        log_level = logging.DEBUG if debug else logging.INFO
        app_log_dir = Path.joinpath(logdir, 'ai_launcher.log')
        print(f"AppLogDir: {app_log_dir}")
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(app_log_dir),
                logging.StreamHandler()  # Still shows in console
            ]
        )

    def _on_stt_hotkey_pressed(self):
        self.show_window()
        QTimer.singleShot(200, self.recording_manager.toggle_recording)

    def _setup_signal_connections(self):
        """Setup Connection Signals"""
        self.state_manager.processing_changed.connect(
            self.on_processing_changed)
        self.state_manager.request_cancelled.connect(self.on_request_cancelled)
        self.state_manager.request_ready.connect(self.send_request)
        self.state_manager.stt_state_changed.connect(self.on_stt_state_changed)
        self.state_manager.recording_completed_sg.connect(
            self.on_recording_completed)
       # UIManager signals (UI state)
        self.ui_manager.expansion_changed.connect(self.on_expanded_changed)
        self.state_manager.clear_multiline_input_sg.connect(
            self.clear_multiline_input)

    # @pyqtSlot(bool)
    # def on_expansion_changed(self, is_expanded):
    #     """Handle UI expansion changes."""
    #     if is_expanded:
    #         # Calculate window size based on input type
    #         if self.ui_manager.is_multiline_input():
    #             width, height = WindowSize.EXPANDED_MULTILINE_INPUT_WIDTH, WindowSize.EXPANDED_MULTILINE_INPUT_HEIGHT
    #         else:
    #             width, height = WindowSize.EXPANDED_SINGLELINE_INPUT_WIDTH, WindowSize.EXPANDED_SINGLELINE_INPUT_HEIGHT
    #         self.animate_resize(width, height)
    #     else:
    #         self.animate_resize(WindowSize.COMPACT_WIDTH,
    #                             WindowSize.COMPACT_HEIGHT)

    def _initialize_core_components(self):
        """Initialize config, API client, etc."""
        self.config = Config()
        self.window_manager = WindowManager(logger, self, self.config)
        self.api_client = ApiClient(logger, self.config)
        self.stt_api_client = None

    def _initialize_managers(self):
        "Initialize managers"
        convrestation_history_limit = self.config.get(
            'message_history_limit', Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT)
        # Initialize managers
        self.conversation_manager = ConversationManager(
            logger, max_conversations=convrestation_history_limit)
        self.style_manager = StyleManager(logger)
        self.animation_manager = AnimationManager(
            self, logger, self.style_manager)
        self.state_manager = StateManager(self.config, logger)
        self.markdown_render = MarkdownRenderer(logger)
        self.hotkey_manager = HotkeyManager(logger, self.config)
        self.recording_manager = Recording_Manager(
            logger, state_manager=self.state_manager, config=self.config)
        self.tray_manager = TrayManager(
            logger, self.show_window, self.hide_window, self.open_settings, self.quit_application)

        self.ui_manager = UIManager(
            self, logger, self.config)
        self.window_manager.setup_window_properties()

    def stt_configure(self):
        """Initialize STT API client with better error handling."""
        self.stt_enabled = self.config.get('stt_enabled', STT.DEFAULT_ENABLED)
        if not self.stt_enabled:
            self.stt_api_client = None
            return

        try:
            if self.stt_api_client is None:
                self.stt_api_client = SttApiClient(logger, self.config)
            logger.info("STT API client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize STT API client: {e}")
            self.stt_enabled = False
            self.stt_api_client = None
            return False

    def _get_signal_callbacks(self):
        """Centralize callback definitions to avoid duplication"""
        return {
            'input_changed': self.on_input_changed,
            'return_pressed': self.force_send_request,
            'stt_clicked': self.recording_manager.toggle_recording,
            'settings_clicked': self.open_settings,
            'copy_clicked': self.copy_response,
            'start_thinking_animation': self.animation_manager.start_thinking_animation,
            'stop_thinking_animation': self.animation_manager.stop_thinking_animation,
            'is_currenlty_expanded': self.ui_manager.is_currently_expanded,
        }

    def _reconnect_ui_signals(self):
        """Reusable signal connection method"""
        self.ui_manager.connect_signals(self._get_signal_callbacks())

    # Remove the old hotkey methods and replace with:
    def restart_hotkey_listener(self):
        """Restart the global hotkey listener with new settings."""
        self.hotkey_manager.restart_listener()

    def quit_application(self):
        """Quit application using WindowManager."""
        self.window_manager.quit_application()

    def show_window(self):
        """Show window using WindowManager."""
        self.window_manager.show_window()

    def hide_window(self):
        """Hide window using WindowManager."""
        self.window_manager.hide_window()

    def setup_ui(self):
        """Setup UI using UIManager."""
        is_multiline = self.config.get(
            'multiline_input', InputSettings.IS_MULTILINE_INPUT)
        self.ui_manager.setup_ui(multiline_input=is_multiline)
        # Connect signals
        self._reconnect_ui_signals()

    def update_stt_button_visibility(self):
        """Update mic button visibility."""
        self.stt_enabled = self.config.get('stt_enabled', STT.DEFAULT_ENABLED)
        self.ui_manager.update_stt_button_visibility(self.stt_enabled)

    def set_input_state(self, state):
        """Set input field state."""
        self.ui_manager.set_input_state(state)

        # Handle animations
        if state == "thinking":
            self.animation_manager.start_thinking_animation(self.ui_manager.input_field)
        else:
            self.animation_manager.stop_thinking_animation()

    def on_input_type_changed(self):
        """Called by UIManager when input type changes"""
        self._reconnect_ui_signals()

    def position_copy_button(self):
        """Position copy button."""
        self.ui_manager.position_copy_button()

    def resizeEvent(self, event):
        """Handle window resize to reposition copy button and adjust response area."""
        super().resizeEvent(event)

        # Reposition copy button
        if hasattr(self, 'copy_button') and self.ui_manager.copy_button.isVisible():
            self.position_copy_button()

        # Dynamically adjust response area constraints based on window size
        if hasattr(self, 'response_area'):
            window_height = self.height()
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

            self.ui_manager.response_area.setMinimumHeight(min_response_height)
            self.ui_manager.response_area.setMaximumHeight(max_response_height)

    def copy_response(self):
        """Copy accumulated response text to clipboard."""
        try:
            response_text = self.state_manager.accumulated_response or self.ui_manager.response_area.toPlainText()
            if response_text.strip():
                clipboard = QApplication.clipboard()
                clipboard.setText(response_text)

                # Visual feedback
                original_text = self.ui_manager.copy_button.text()
                self.ui_manager.copy_button.setText(Text.COPY_SUCCESS)
                self.ui_manager.copy_button.setStyleSheet(
                    self.style_manager.button_styles.get_copy_button_success_style())

                QTimer.singleShot(Timing.COPY_FEEDBACK_DURATION, lambda: (
                    self.ui_manager.copy_button.setText(original_text),
                    self.ui_manager.copy_button.setStyleSheet("")
                ))
            else:
                self.show_status(Text.STATUS_NO_TEXT_TO_COPY)

        except Exception as e:
            logger.error(f"{Text.ERROR_COPYING_CLIPBOARD} {str(e)}")
            self.show_status(Text.STATUS_COPY_FAILED)

    def animate_resize(self, width, height, fast=False):
        """Animate window resize using WindowManager."""
        self.window_manager.animate_resize(width, height, fast)

    def apply_modern_style(self):
        """Apply the modern stylesheet using StyleManager."""
        self.setStyleSheet(
            self.style_manager.get_complete_style(self.current_theme))

    def _cleanup_worker(self):
        """Cleanup worker thread safely."""
        if self.state_manager.streaming_worker:
            if self.state_manager.streaming_worker.isRunning():
                self.state_manager.streaming_worker.terminate()
            self.state_manager.streaming_worker = None

    def cancel_current_request(self):
        """Cancel current request - delegates to StateManager."""
        if not self.state_manager.is_processing:
            return

        # StateManager handles worker cleanup and state management
        self.state_manager.cancel_current_request()

        # Additional UI cleanup if needed
        if hasattr(self.api_client, 'cancel_request'):
            try:
                self.api_client.cancel_request()
            except Exception as e:
                logger.error(f"Error cancelling API request: {e}")

    @pyqtSlot(str)
    def send_request(self, prompt):
        """Send request - called by StateManager signal."""
        logger.debug(f"Sending request with prompt length: {len(prompt)}")

        if not prompt or self.state_manager.is_currently_processing():
            logger.debug(
                "Request blocked - empty prompt or already processing")
            return

        # Store the current prompt for conversation history
        self.current_user_prompt = prompt

        # Start processing (application logic)

        # Update UI state (visual feedback)
        request_id = self.state_manager.start_processing()
        self.ui_manager.set_visual_state("thinking")

        logger.debug(f"Started processing with request_id: {request_id}")

        # Execute request
        QTimer.singleShot(50, lambda: self._execute_request(request_id))

    @pyqtSlot(str)
    def on_stt_state_changed(self, state):
        """Handle STT state changes."""
        logger.debug(f"STT state changed to: {state}")

        if state == "recording":
            self.ui_manager.stt_button.setObjectName("sttButtonRecording")
            self.update_stt_button_appearance(state)
        elif state == "idle":
            self.ui_manager.stt_button.setObjectName("sttButton")
            self.update_stt_button_appearance(state)
        else:
            logger.info("Wrong State when updating stt button")

    @pyqtSlot()
    def clear_multiline_input(self):
        """Clear Input"""
        self.ui_manager.handle_multiline_resize()

    @pyqtSlot()
    def on_recording_completed(self):
        # Get transcribed text and fill the input field
        transcribed_text = self.stt_api_client.transcribe()
        if transcribed_text and transcribed_text.strip():
            self.ui_manager.input_field.setText(transcribed_text)
            # Optionally set focus back to input field
            self.ui_manager.input_field.setFocus()
            if self.ui_manager.is_multiline_input():
                self.ui_manager.handle_multiline_resize()

    def update_stt_button_appearance(self, state):
        """Update STT button appearance based on state."""
        # self.ui_manager.stt_button.setStyle(self.ui_manager.stt_button.style())
        if state == "recording":
            self.ui_manager.stt_button.setIcon(QIcon(str(Files.MIC_RECORDING_ICON_PATH)))
            self.ui_manager.stt_button.style().unpolish(self.ui_manager.stt_button)
            self.ui_manager.stt_button.style().polish(self.ui_manager.stt_button)
        elif state == "idle":
            self.ui_manager.stt_button.setIcon(QIcon(str(Files.MIC_IDLE_ICON_PATH)))
            self.ui_manager.stt_button.style().unpolish(self.ui_manager.stt_button)
            self.ui_manager.stt_button.style().polish(self.ui_manager.stt_button)

    def _update_response_display(self):
        """Update response display with basic markdown formatting."""
        response_text = self.state_manager.get_accumulated_response()

        # Convert basic markdown to HTML
        html_content = self.markdown_render._basic_markdown_to_html(
            response_text)
        self.ui_manager.response_area.setHtml(html_content)

    def _handle_request_lifecycle(self, request_id, action):
        """Centralized request lifecycle management."""
        if not self.state_manager.is_request_valid(request_id):
            logger.debug(f"Invalid request_id {request_id}, ignoring {action}")
            return False
        return True

    def _handle_chunk(self, chunk, request_id):
        """Handle incoming response chunks."""
        if not self._handle_request_lifecycle(request_id, "chunk"):
            return
        try:
            self.state_manager.add_response_chunk(chunk)
            if not self.ui_manager.is_response_visible():
                self.ui_manager.expand_ui()
            self._update_response_display()
            self._auto_scroll_response()
        except Exception as e:
            logger.error(f"Error handling chunk: {e}")
            self._handle_error(
                f"Error processing response: {str(e)}", request_id)

    def _auto_scroll_response(self):
        """Separate auto-scroll logic."""
        cursor = self.ui_manager.response_area.textCursor()
        cursor.movePosition(cursor.End)
        self.ui_manager.response_area.setTextCursor(cursor)

    def _handle_completion(self, request_id):
        """Handle request completion with conversation storage."""
        if not self.state_manager.handle_completion(request_id):
            return
        # Get the complete response
        full_response = self.state_manager.get_accumulated_response()

        if hasattr(self, 'current_user_prompt') and full_response:
            self.conversation_manager.add_conversation(
                self.current_user_prompt, full_response)
            logger.debug("Conversation added to history")

        # Final update of response
        self._update_response_display()

        # Return UI to normal state
        self.ui_manager.set_visual_state("normal")
        self.ui_manager.settings_button.setEnabled(True)
        self.ui_manager.input_field.setFocus()

    def _handle_error(self, error_message, request_id):
        """Handle errors with validation."""
        logger.error(f"Request {request_id} failed: {error_message}")
        if not self.state_manager.handle_error(error_message, request_id):
            return

        # Get error text from StateManager
        error_text = self.state_manager.get_accumulated_response()

        # Update UI - expand if not visible
        if not self.ui_manager.is_response_visible():
            self.ui_manager.expand_ui()

        # Display error
        self.ui_manager.response_area.setHtml(error_text)

        # Return UI to normal state
        self.ui_manager.set_visual_state("normal")
        self.ui_manager.settings_button.setEnabled(True)
        self.ui_manager.input_field.setFocus()

        # Clean up worker through StateManager
        self.state_manager.cleanup_worker_safely()

    def _execute_request(self, request_id):
        """Execute request using StateManager's worker creation."""
        try:
            # Get conversation history for context (Launcher responsibility)
            conversation_history = self.conversation_manager.get_conversation_history()

            # Create worker through StateManager (StateManager responsibility)
            worker = self.state_manager.create_streaming_worker(
                api_client=self.api_client,
                request_id=request_id,
                conversation_history=conversation_history
            )
            if not worker:
                logger.error("Failed to create streaming worker")
                self._handle_error(
                    "Failed to create request worker", request_id)
                return

            worker.chunk_received.connect(
                lambda chunk: self._handle_chunk(chunk, request_id)
            )
            worker.response_complete.connect(
                lambda: self._handle_completion(request_id)
            )
            worker.error_occurred.connect(
                lambda error: self._handle_error(error, request_id)
            )

            # Start the worker
            worker.start()

        except Exception as e:
            logger.error(f"Error executing request: {e}")
            self._handle_error(str(e), request_id)

    @pyqtSlot()
    def on_response_complete(self):
        """Handle response completion."""
        self.state_manager.is_processing = False
        self.show_status(Text.STATUS_COMPLETE)

        # Re-enable settings button
        self.ui_manager.settings_button.setEnabled(True)
        self.ui_manager.input_field.setFocus()

        # Hide status after a moment
        QTimer.singleShot(Timing.STATUS_HIDE_DELAY, self.hide_status)

    @pyqtSlot(bool)
    def on_expanded_changed(self, is_expanded):
        """Handle expansion state changes from StateManager."""
        if is_expanded:
            if self.ui_manager.is_multiline_input():
                expanded_width = WindowSize.EXPANDED_MULTILINE_INPUT_WIDTH
                expanded_height = WindowSize.EXPANDED_MULTILINE_INPUT_HEIGHT
            else:
                expanded_width = WindowSize.EXPANDED_SINGLELINE_INPUT_WIDTH
                expanded_height = WindowSize.EXPANDED_SINGLELINE_INPUT_HEIGHT

            self.animate_resize(expanded_width, expanded_height)
            self.ui_manager.show_response_area()
        else:
            self.animate_resize(WindowSize.COMPACT_WIDTH,
                                WindowSize.COMPACT_HEIGHT)
            QTimer.singleShot(10, lambda: (
                self.ui_manager.response_area.setVisible(False)
            ))
            QTimer.singleShot(30, lambda: (
                self.ui_manager.copy_button.setVisible(False)
            ))


    def show_status(self, message):
        """Print status instead of showing in UI."""
        pass

    def hide_status(self):
        """No-op since we don't have a status label."""
        pass

    def on_theme_changed(self, new_theme):
        """Handle theme change signal from settings dialog."""
        self.current_theme = new_theme
        self.style_manager.set_theme(new_theme)
        self.apply_modern_style()

    def on_stt_settings_changed(self):
        """STT settings change"""
        logger.info("STT Settings Changed")
        self.stt_configure()
        self.update_stt_button_visibility()
        self.stt_api_client = SttApiClient(logger, self.config)

    def open_settings(self):
        """Open the settings dialog."""
        logger.debug("Opening settings dialog")
        dialog: SettingsDialog = SettingsDialog(logger, self.config, self)
        # Connect the theme change signal
        dialog.theme_changed.connect(self.on_theme_changed)
        # Let the dialog calculate its size first
        dialog.adjustSize()

        # Center the dialog relative to the main window
        main_rect = self.geometry()
        dialog_rect = dialog.geometry()
        center_x = main_rect.x() + (main_rect.width() - dialog_rect.width()) // 2
        center_y = main_rect.y() + (main_rect.height() - dialog_rect.height()) // 2
        dialog.move(center_x, center_y)
        if dialog.exec_():
            logger.debug("Settings dialog accepted, processing changes")
            
            # Check if multiline setting changed
            old_multiline = self.ui_manager.is_multiline_input()
            new_multiline = self.config.get('multiline_input', False)
            logger.debug(f"Multiline input - old: {old_multiline}, new: {new_multiline}")
            
            if new_multiline != old_multiline:
                logger.info(f"Multiline input mode changing from {old_multiline} to {new_multiline}")
                self.state_manager.set_input_type(new_multiline)
                logger.debug("State manager updated with new input type")
                
                # Update button appearance
                self.ui_manager.update_multiline_toggle_button(new_multiline)
                logger.debug("Multiline toggle button appearance updated")
                
                # Recreate UI with new input mode
                self.ui_manager.recreate_input_field(new_multiline)
                logger.debug("Input field recreated with new mode")
                
                # Reconnect signals
                self.ui_manager.connect_signals(self._get_signal_callbacks)
                logger.debug("UI signals reconnected")

            # Check theme changes
            old_theme = self.current_theme
            new_theme = self.config.get('theme', Theme.DEFAULT_THEME)
            logger.debug(f"Theme - old: {old_theme}, new: {new_theme}")
            
            if new_theme != old_theme:
                logger.info(f"Theme changing from {old_theme} to {new_theme}")
                self.current_theme = new_theme
                self.style_manager.set_theme(self.current_theme)
                logger.debug("Style manager updated with new theme")
                self.apply_modern_style()
                logger.debug("Modern style applied")

            # Show feedback with larger, visible status
            delay_seconds = self.config.get(
                'request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS)
            status_msg = f"✓ Settings saved! Request delay: {delay_seconds}s"
            logger.info(f"Settings saved successfully - request delay: {delay_seconds}s")
            self.show_status(status_msg)

            # Update API client
            logger.debug("Updating API client with new configuration")
            self.api_client = ApiClient(logger, self.config)
            logger.debug("API client updated")
            
            logger.debug("Restarting hotkey listener")
            self.restart_hotkey_listener()
            logger.debug("Hotkey listener restarted")

            # Hide status after longer delay
            QTimer.singleShot(
                Timing.SETTINGS_FEEDBACK_DURATION, self.hide_status)
            logger.debug(f"Status hide timer set for {Timing.SETTINGS_FEEDBACK_DURATION}ms")
        else:
            logger.debug("Settings dialog cancelled by user")
    def closeEvent(self, event):
        """Override close event to hide to tray instead of quitting."""
        self.window_manager.handle_close_event(event)

    def mousePressEvent(self, event):
        """Enable window dragging and resizing."""
        self.window_manager.handle_mouse_press(event)

    def mouseMoveEvent(self, event):
        """Handle window dragging and resizing."""
        self.window_manager.handle_mouse_move(event)

    def leaveEvent(self, event):
        """Reset cursor when mouse leaves window."""
        self.window_manager.handle_leave_event(event)
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        """Clean up after mouse release."""
        self.window_manager.handle_mouse_release(event)

    def lmoveEvent(self, event):
        """Handle any window move event."""
        super().moveEvent(event)
        self.window_manager.handle_move_event(event)

    def on_state_changed(self, new_state):
        """Handle state changes from StateManager."""
        logger.debug(f"State changed to: {new_state}")
        self.set_input_state(new_state)

        if new_state == "normal" and not self.state_manager.get_current_prompt():
            logger.debug(
                "State is normal with no prompt - checking if response should be hidden")
            # if self.ui_manager.response_area.isVisible():
            #     logger.debug("Hiding response area")
            #     self.ui_manager.hide_response()

    def on_processing_changed(self, is_processing):
        """Handle processing state changes from StateManager."""
        logger.debug(
            f"Processing state changed: {'started' if is_processing else 'stopped'}")
        self.ui_manager.settings_button.setEnabled(not is_processing)

    def on_response_ready(self, response):
        """Handle when response is ready to display."""
        logger.debug(f"Response ready, length: {len(response)} characters")
        self.ui_manager.response_area.setHtml(response)

    def on_request_cancelled(self):
        """Handle request cancellation from StateManager."""
        logger.debug("Request cancelled - resetting UI state")
        self.ui_manager.set_visual_state("normal")
        self.ui_manager.settings_button.setEnabled(True)

    def on_input_changed(self, text):
        """
        Handle input changes - coordinate between StateManager and UIManager.
        This is where the coordination happens.
        """
        logger.debug(f"Input changed, length: {len(text)} characters")
        self.state_manager.set_prompt(text, self.ui_manager.is_multiline_input())

        if text.strip():
            self.ui_manager.set_visual_state("typing")
        else:
            self.ui_manager.set_visual_state("normal")
            # if self.ui_manager.is_currently_expanded():
                # self.ui_manager.contract_ui()
            self.ui_manager.hide_response()

        if not text.strip() and self.ui_manager.is_multiline_input():
            self.ui_manager.handle_multiline_resize()

    def force_send_request(self):
        """Delegate to StateManager."""
        logger.debug("Force send request triggered (Enter key pressed)")
        self.state_manager.force_send_request()

    # Add event filter for handling key presses

    def eventFilter(self, obj, event):
        """Handle key events for input field."""
        if obj == self.ui_manager.input_field and event.type() == event.KeyPress:
            if self.ui_manager.is_multiline_input():
                # Multi-line mode: Ctrl+Enter submits
                if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and event.modifiers() == Qt.ControlModifier:
                    self.force_send_request()
                    return True
            else:
                # Single-line mode: Enter submits
                if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and event.modifiers() == Qt.NoModifier:
                    self.force_send_request()
                    return True
        return super().eventFilter(obj, event)
