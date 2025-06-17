# Add missing imports at the top
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QAction, QShortcut, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence

from managers.recording_manager import RecordingManager
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
from managers.state_manager import StateManager
from utils.stt_api_client import SttApiClient


class Launcher(QMainWindow):
    def __init__(self, logdir: str, debug=False):
        super().__init__()

        self._setup_logging(logdir, debug)
        self.logger = logging.getLogger(__name__)

        self._initialize_core_components()
        self._initialize_managers()
        self._setup_signal_connections()
        self.current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        self.style_manager.set_theme(self.current_theme)
        self.ui_manager.setup_ui(self.conversation_manager)

        self._reconnect_ui_signals()
        self.stt_configure()
        self.update_stt_button_visibility()
        self.apply_modern_style()
        self.tray_manager.setup_system_tray()
        # Flag to track if app should really quit
        self.should_quit = False
        self.hotkey_manager.setup_hotkey()
        self.hotkey_manager.hotkey_pressed.connect(self.show_window)
        self.hotkey_manager.stt_hotkey_pressed.connect(self._on_stt_hotkey_pressed)

    def _setup_logging(self, logdir, debug):
        """Setup logging configuration."""
        from logging.handlers import TimedRotatingFileHandler
        
        log_level = logging.DEBUG if debug else logging.INFO
        app_log_dir = Path.joinpath(logdir, 'ai_launcher.log')
        print(f"AppLogDir: {app_log_dir}")
        
        # Create timed rotating file handler
        file_handler = TimedRotatingFileHandler(
            app_log_dir,
            when='midnight',
            interval=1,
            backupCount=15,
            encoding='utf-8'
        )
        # Custom namer to ensure .log extension
        file_handler.namer = lambda name: name.replace('.log.', '_') + '.log'
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                file_handler,
                logging.StreamHandler()
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
        # STT Recording Signals
        self.recording_manager.recording_started.connect(self.on_stt_recording)
        self.recording_manager.recording_stopped.connect(self.on_recording_completed)
        self.recording_manager.recording_failed.connect(self.on_recording_failed)
       # UIManager signals (UI state)
        self.ui_manager.expansion_changed.connect(self.on_expanded_changed)

    def _initialize_core_components(self):
        """Initialize config, API client, etc."""
        self.config = Config()
        self.api_client = ApiClient(self.config)
        self.stt_api_client = None
        self.window_manager = WindowManager(self.config)

    def _initialize_managers(self):
        """Initialize managers"""
        conversation_history_limit = self.config.get(
            'message_history_limit', Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT)
        # Initialize managers
        self.conversation_manager = ConversationManager(
            max_conversations=conversation_history_limit)
        self.style_manager = StyleManager()
        self.animation_manager = AnimationManager(
            self, self.style_manager)
        self.state_manager = StateManager(self.config)
        self.hotkey_manager = HotkeyManager(self.config)
        self.recording_manager = RecordingManager(
            state_manager=self.state_manager, config=self.config)
        self.tray_manager = TrayManager(
            self.show_window, self.hide_window, self.open_settings, self.quit_application)
        self.ui_manager = UIManager(
            self, self.config, self.style_manager)
        
        # Set up WindowManager after window exists
        self.window_manager.set_window(self)
        self.window_manager.setup_window_properties()
        
        # Connect WindowManager signals
        self.window_manager.tray_message_requested.connect(
            self._on_tray_message_requested
        )
        self.window_manager.window_minimized.connect(
            self._on_window_minimized
        )
        self.window_manager.window_restored.connect(
            self._on_window_restored
        )

    def _on_tray_message_requested(self, title, message):
        """Handle tray message request from WindowManager"""
        try:
            if hasattr(self, 'tray_manager') and self.tray_manager:
                self.tray_manager.show_message(title, message)
                self.logger.debug(f"Tray message shown: {title} - {message}")
            else:
                self.logger.warning("TrayManager not available for message display")
        except Exception as e:
            self.logger.error(f"Error showing tray message: {e}")

    def _on_window_minimized(self):
        """Handle window minimized event"""
        self.logger.debug("Window minimized - checking clear settings")
        # You can add any logic here for when window is minimized
        self.logger.info("Hiding window to system tray")
        
        # Show tray message if tray is available
        if hasattr(self.tray_manager, 'tray_icon'):
            self.logger.debug("Showing background tray message")
        else:
            self.logger.debug("No tray manager available for background message")
        
        # Clear history if configured
        clear_history_on_minimize = self.config.get('clear_history_on_minimize', False)
        if clear_history_on_minimize:
            self.logger.debug("Clearing conversation history (config enabled)")
            self.conversation_manager.clear_current_conversation()

        # Check if we should clear response on minimize
        clear_on_minimize = self.config.get('clear_on_minimize', False)
        if clear_on_minimize:
            self.logger.debug("Clearing previous response on window show (config enabled)")
            self.ui_manager.clear_response_on_minimize()
        
        self.logger.info("Window hidden successfully")
        
    def _on_window_restored(self):
        """Handle window restored from minimized state"""
        self.logger.debug("Window restored from minimized state")

        # Focus on input field
        if hasattr(self.ui_manager, 'input_field'):
            self.ui_manager.input_field.setFocus()
            self.logger.debug("Input field focused")
        else:
            self.logger.debug("No input field to focus")
            
        self.logger.info("Window shown successfully")


    def stt_configure(self):
        """Initialize STT API client with better error handling."""
        self.stt_enabled = self.config.get('stt_enabled', STT.DEFAULT_ENABLED)
        if not self.stt_enabled:
            self.stt_api_client = None
            return

        try:
            if self.stt_api_client is None:
                self.stt_api_client = SttApiClient(self.config)
            self.logger.info("STT API client initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize STT API client: {e}")
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
            'start_thinking_animation': self.animation_manager.start_thinking_animation,
            'stop_thinking_animation': self.animation_manager.stop_thinking_animation,
        }
    def _get_signal_input_callbacks(self):
        """Centralize callback definitions to avoid duplication"""
        return {
            'input_changed': self.on_input_changed,
            'return_pressed': self.force_send_request,
        }

    def _reconnect_ui_signals(self):
        """Reusable signal connection method"""
        self.ui_manager.connect_signals(self._get_signal_callbacks())

    def _reconnect_input_signals(self):
        """Reusable signal connection method"""
        self.ui_manager.connect_input_signals(self._get_signal_input_callbacks())

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
        self._reconnect_input_signals()

    def resizeEvent(self, event):
        """Handle window resize - delegate to UIManager."""
        super().resizeEvent(event)
        
        # Let UIManager handle all resize-related UI updates
        if hasattr(self, 'ui_manager'):
            self.ui_manager.handle_window_resize(self.size())

    def animate_resize(self, width, height, fast=False):
        """Animate window resize using WindowManager."""
        self.logger.debug(f"Animating resize to {width}x{height}, fast={fast}")
        self.animation_manager.animate_window_resize(self, width, height, fast)
        # self.window_manager.animate_resize(width, height, fast)

    def apply_modern_style(self):
        """Apply the modern stylesheet using StyleManager."""
        self.setStyleSheet(
            self.style_manager.get_complete_style(self.current_theme))
        self.ui_manager.reapply_conversation_history_theme()


    @pyqtSlot(str)
    def send_request(self, prompt):
        """Send request - called by StateManager signal."""
        self.logger.debug(f"Sending request with prompt length: {len(prompt)}")

        if not prompt or self.state_manager.is_currently_processing():
            self.logger.debug(
                "Request blocked - empty prompt or already processing")
            return

        # Store the current prompt for conversation history
        self.current_user_prompt = prompt

        # Start processing (application logic)

        # Update UI state (visual feedback)
        request_id = self.state_manager.start_processing()
        self.ui_manager.set_visual_state("thinking")

        self.logger.debug(f"Started processing with request_id: {request_id}")

        # Execute request
        QTimer.singleShot(50, lambda: self._execute_request(request_id))

    @pyqtSlot()
    def on_stt_recording(self):
        """Handle STT state changes."""
        self.logger.debug(f"STT recording.")
        self.ui_manager.stt_button.setObjectName("sttButtonRecording")
        self.ui_manager.update_stt_button_appearance("recording")

    @pyqtSlot()
    def on_recording_completed(self):
        self.stt_idle()
        try:
            # Get transcribed text and fill the input field
            transcribed_text = self.stt_api_client.transcribe()
            if transcribed_text and transcribed_text.strip():
                self.ui_manager.input_field.setText(transcribed_text)
                # Optionally set focus back to input field
                self.ui_manager.input_field.setFocus()
                if self.ui_manager.is_multiline_input():
                    self.ui_manager.handle_multiline_resize()
        except Exception as e:
            # Log the error and optionally show user feedback
            self.logger.error(f"Failed to transcribe audio: {str(e)}")
            self.ui_manager.show_error_message(f"Transcription failed: {str(e)}")
    
    def stt_idle(self):
        """Handle STT state changes."""
        self.logger.debug(f"STT idle.")
        self.ui_manager.stt_button.setObjectName("sttButton")
        self.ui_manager.update_stt_button_appearance("idle")

    @pyqtSlot()
    def on_recording_failed(self):
        error_message = "Failed while STT Recording!"
        self.ui_manager.show_error_message(f"Error: {error_message}")


    def _update_response_display(self):
        """Update response display with basic markdown formatting."""
        response_text = self.state_manager.get_accumulated_response()
        self.logger.debug(f"accumulated response unformatted: \n{response_text}")

        if not self.ui_manager.is_conversation_visible():
            self.ui_manager.show_conversation_area()
        else:
            self.ui_manager.set_response_text(response_text)

    def _handle_request_lifecycle(self, request_id, action):
        """Centralized request lifecycle management."""
        if not self.state_manager.is_request_valid(request_id):
            self.logger.debug(f"Invalid request_id {request_id}, ignoring {action}")
            return False
        return True

    def _handle_chunk(self, chunk, request_id):
        """Handle incoming response chunks."""
        if not self._handle_request_lifecycle(request_id, "chunk"):
            return
        try:
            self.state_manager.add_response_chunk(chunk)
            if not self.ui_manager.is_conversation_visible():
                self.ui_manager.show_conversation_area()
            self._update_response_display()
            self._auto_scroll_response()
        except Exception as e:
            self.logger.error(f"Error handling chunk: {e}")
            self._handle_error(
                f"Error processing response: {str(e)}", request_id)

    def _auto_scroll_response(self):
        """Separate auto-scroll logic."""
        self.ui_manager.auto_scroll()

    def _handle_completion(self, request_id):
        """Handle request completion with conversation storage."""
        if not self.state_manager.handle_completion(request_id):
            return
        # Get the complete response
        full_response = self.state_manager.get_accumulated_response()

        if hasattr(self, 'current_user_prompt') and full_response:
            self.conversation_manager.add_conversation(
                self.current_user_prompt, full_response)
            self.logger.debug("Conversation added to history")

        # Final update of response
        self._update_response_display()

        # Return UI to normal state
        self.ui_manager.set_visual_state("normal")
        self.ui_manager.settings_button.setEnabled(True)
        self.ui_manager.input_field.setFocus()

    def _handle_error(self, error_message, request_id=None):
        """Handle errors during API calls."""
        try:
            self.logger.error(f"API Error (request_id: {request_id}): {error_message}")
            
            # Update UI state
            self.ui_manager.set_visual_state("error")
            
            # Show error in conversation area through UIManager delegation
            error_text = f"<p style='color: red;'><strong>Error:</strong> {error_message}</p>"
            self.ui_manager.set_response_text(error_text)  # Use delegation method
            
            # Show conversation area if not visible
            if not self.ui_manager.is_conversation_visible():
                self.ui_manager.show_conversation_area()
            
            # Show error message popup
            self.ui_manager.show_error_message(f"Error: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error in _handle_error: {e}")
            # Fallback: just show error popup
            self.ui_manager.show_error_message(f"Error: {error_message}")

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
                self.logger.error("Failed to create streaming worker")
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
            self.logger.error(f"Error executing request: {e}")
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
            self.ui_manager.show_conversation_area()
        else:
            self.animate_resize(WindowSize.COMPACT_WIDTH,
                                WindowSize.COMPACT_HEIGHT)
            QTimer.singleShot(10, lambda: (
                self.ui_manager.hide_conversation_area()
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
        self.logger.info("STT Settings Changed")
        self.stt_configure()
        self.update_stt_button_visibility()

    def open_settings(self):
        """Open the settings dialog."""
        self.logger.debug("Opening settings dialog")
        dialog: SettingsDialog = SettingsDialog(self.config, self)
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
            self.logger.debug("Settings dialog accepted, processing changes")
            
            # Check if multiline setting changed
            old_multiline = self.ui_manager.is_multiline_input()
            new_multiline = self.config.get('multiline_input', False)
            self.logger.debug(f"Multiline input - old: {old_multiline}, new: {new_multiline}")
            
            if new_multiline != old_multiline:
                self.logger.info(f"Multiline input mode changing from {old_multiline} to {new_multiline}")
                self.ui_manager.set_input_type(new_multiline)
                self.logger.debug("State manager updated with new input type")
                
                # Update button appearance
                self.ui_manager.update_multiline_toggle_button(new_multiline)
                self.logger.debug("Multiline toggle button appearance updated")
                
                # Recreate UI with new input mode
                self.ui_manager.recreate_input_field(new_multiline)
                self.logger.debug("Input field recreated with new mode")
                
                # Reconnect signals
                self.ui_manager.connect_signals(self._get_signal_callbacks)
                self.logger.debug("UI signals reconnected")

            # Check theme changes
            old_theme = self.current_theme
            new_theme = self.config.get('theme', Theme.DEFAULT_THEME)
            self.logger.debug(f"Theme - old: {old_theme}, new: {new_theme}")
            
            if new_theme != old_theme:
                self.logger.info(f"Theme changing from {old_theme} to {new_theme}")
                self.current_theme = new_theme
                self.style_manager.set_theme(self.current_theme)
                self.logger.debug("Style manager updated with new theme")
                self.apply_modern_style()
                self.logger.debug("Modern style applied")

            # Show feedback with larger, visible status
            delay_seconds = self.config.get(
                'request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS)
            status_msg = f"✓ Settings saved! Request delay: {delay_seconds}s"
            self.logger.info(f"Settings saved successfully - request delay: {delay_seconds}s")
            self.show_status(status_msg)

            # Update API client
            self.logger.debug("Updating API client with new configuration")
            self.api_client = ApiClient(self.config)
            self.logger.debug("API client updated")
            
            self.logger.debug("Restarting hotkey listener")
            self.restart_hotkey_listener()
            self.logger.debug("Hotkey listener restarted")

            # Hide status after longer delay
            QTimer.singleShot(
                Timing.SETTINGS_FEEDBACK_DURATION, self.hide_status)
            self.logger.debug(f"Status hide timer set for {Timing.SETTINGS_FEEDBACK_DURATION}ms")
        else:
            self.logger.debug("Settings dialog cancelled by user")
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

    def moveEvent(self, event):
        """Handle any window move event."""
        super().moveEvent(event)
        self.window_manager.handle_move_event(event)

    def on_state_changed(self, new_state):
        """Handle state changes from StateManager."""
        self.logger.debug(f"State changed to: {new_state}")
        self.set_input_state(new_state)

        if new_state == "normal" and not self.state_manager.get_current_prompt():
            self.logger.debug(
                "State is normal with no prompt - checking if response should be hidden")

    def on_processing_changed(self, is_processing):
        """Handle processing state changes from StateManager."""
        self.logger.debug(
            f"Processing state changed: {'started' if is_processing else 'stopped'}")
        self.ui_manager.settings_button.setEnabled(not is_processing)

    def on_response_ready(self, response):
        """Handle when response is ready to display."""
        self.logger.debug(f"Response ready, length: {len(response)} characters")
        self.ui_manager.conversation_area.setHtml(response)

    def on_request_cancelled(self):
        """Handle request cancellation from StateManager."""
        self.logger.debug("Request cancelled - resetting UI state")
        self.ui_manager.set_visual_state("normal")
        self.ui_manager.settings_button.setEnabled(True)

    def on_input_changed(self, text):
        """
        Handle input changes - coordinate between StateManager and UIManager.
        This is where the coordination happens.
        """
        self.logger.debug(f"Input changed, length: {len(text)} characters")
        self.state_manager.set_prompt(text, self.ui_manager.is_multiline_input())

        self.ui_manager.on_input_changed(text)



    def force_send_request(self):
        """Delegate to StateManager."""
        self.logger.debug("Force send request triggered (Enter key pressed)")
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


