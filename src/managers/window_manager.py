import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from utils.constants import WindowSize, ElementSize

class WindowManager:
    def __init__(self, logger,  main_window, config):
        self.logger:logging.Logger = logger.getChild('window_manager')
        self.main_window = main_window
        self.config = config
        
        # Window state tracking
        self.resize_direction = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.drag_position = None
        self.should_quit = False
        
        # Position save timer to debounce position saving
        self.position_save_timer = QTimer()
        self.position_save_timer.setSingleShot(True)
        self.position_save_timer.timeout.connect(self.save_geometry)
        
        self.logger.info("WindowManager initialized")

    def setup_window_properties(self):
        """Set up basic window properties."""
        self.logger.info("Setting up window properties")
        self.main_window.setWindowTitle("AI Assistant")
        self.main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.main_window.setAttribute(Qt.WA_TranslucentBackground)
        self.main_window.setMinimumSize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)
        self.main_window.resize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)
        self.logger.debug(f"Window properties set - Size: {WindowSize.COMPACT_WIDTH}x{WindowSize.COMPACT_HEIGHT}")

    def show_window(self):
        """Show and raise the window to front."""
        try:
            self.logger.info("Showing window")
            
            # Check if we should clear previous response when reopening
            clear_on_minimize = self.config.get('clear_last_response_on_minimize', False)
            if clear_on_minimize:
                self.logger.debug("Clearing previous response on window show (config enabled)")
                self._clear_response_on_show()

            self.logger.debug(f"Window position before show: ({self.main_window.x()}, {self.main_window.y()})")
            
            # Ensure window is visible
            if self.main_window.isMinimized():
                self.logger.debug("Window was minimized, restoring")
                self.main_window.setWindowState(self.main_window.windowState() & ~Qt.WindowMinimized)
            
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Focus on input field
            if hasattr(self.main_window, 'input_field'):
                self.main_window.input_field.setFocus()
                self.logger.debug("Input field focused")
            else:
                self.logger.debug("No input field to focus")
                
            self.logger.info("Window shown successfully")
                
        except Exception as e:
            self.logger.error(f"Error showing window: {e}", exc_info=True)
            # Fallback
            self.main_window.show()
            if hasattr(self.main_window, 'input_field'):
                self.main_window.input_field.setFocus()

    def hide_window(self):
        """Hide the window to system tray."""
        self.logger.info("Hiding window to system tray")
        self.main_window.hide()
        
        # Show tray message if tray is available
        if hasattr(self.main_window, 'tray_manager') and hasattr(self.main_window.tray_manager, 'tray_icon'):
            self.logger.debug("Showing background tray message")
            self.main_window.tray_manager.show_background_message()
        else:
            self.logger.debug("No tray manager available for background message")
        
        # Clear history if configured
        clear_history_on_minimize = self.config.get('clear_history_on_minimize', False)
        if clear_history_on_minimize and hasattr(self.main_window, 'conversation_manager'):
            self.logger.debug("Clearing conversation history (config enabled)")
            self.main_window.conversation_manager.clear_history()
        elif clear_history_on_minimize:
            self.logger.debug("Clear history enabled but no conversation manager found")
        
        self.logger.info("Window hidden successfully")

    def _clear_response_on_show(self):
        """Clear response and reset window when showing."""
        self.logger.debug("Clearing response and resetting window state")
        
        if hasattr(self.main_window, 'response_area'):
            self.main_window.response_area.setHtml("")
            self.main_window.response_area.setVisible(False)
            self.logger.debug("Response area cleared and hidden")
        
        if hasattr(self.main_window, 'copy_button'):
            self.main_window.copy_button.setVisible(False)
            self.logger.debug("Copy button hidden")
        
        # Reset to compact size
        if hasattr(self.main_window, 'animate_resize'):
            self.logger.debug("Animating resize to compact size")
            self.main_window.animate_resize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT, fast=True)
        
        # Clear state manager response
        if hasattr(self.main_window, 'state_manager'):
            if hasattr(self.main_window.state_manager, 'accumulated_response'):
                self.main_window.state_manager.accumulated_response = ""
                self.logger.debug("State manager response cleared")
        
        # Clear input and conversation
        if hasattr(self.main_window, 'input_field'):
            self.main_window.input_field.clear()
            self.logger.debug("Input field cleared")
        
        if hasattr(self.main_window, 'conversation_manager'):
            self.main_window.conversation_manager.clear_history()
            self.logger.debug("Conversation history cleared")

    def quit_application(self):
        """Properly quit the application."""
        self.logger.info("Quitting application")
        self.should_quit = True
        
        if hasattr(self.main_window, 'tray_manager') and hasattr(self.main_window.tray_manager, 'tray_icon'):
            self.logger.debug("Hiding tray icon")
            self.main_window.tray_manager.tray_icon.hide()
        
        self.logger.debug("Calling QApplication.quit()")
        QApplication.quit()

    def get_resize_direction(self, pos):
        """Determine resize direction based on mouse position."""
        rect = self.main_window.rect()

        left = pos.x() <= ElementSize.TRIGGER_EDGE_RESIZE_MARGIN_HORIZONTAL
        right = pos.x() >= rect.width() - ElementSize.TRIGGER_EDGE_RESIZE_MARGIN_HORIZONTAL
        top = pos.y() <= 0
        bottom = pos.y() >= rect.height() - ElementSize.TRIGGER_EDGE_RESIZE_MARGIN_VERTICAL
        
        direction = None
        if top and left:
            direction = "top-left"
        elif top and right:
            direction = "top-right"
        elif bottom and left:
            direction = "bottom-left"
        elif bottom and right:
            direction = "bottom-right"
        elif left:
            direction = "left"
        elif right:
            direction = "right"
        elif top:
            direction = "top"
        elif bottom:
            direction = "bottom"
        
        if direction:
            self.logger.debug(f"Resize direction detected: {direction} at pos ({pos.x()}, {pos.y()})")
        
        return direction

    def update_cursor(self, direction):
        """Update cursor based on resize direction."""
        if direction == "top-left" or direction == "bottom-right":
            self.main_window.setCursor(Qt.SizeFDiagCursor)
        elif direction == "top-right" or direction == "bottom-left":
            self.main_window.setCursor(Qt.SizeBDiagCursor)
        elif direction == "left" or direction == "right":
            self.main_window.setCursor(Qt.SizeHorCursor)
        elif direction == "top" or direction == "bottom":
            self.main_window.setCursor(Qt.SizeVerCursor)
        else:
            self.main_window.setCursor(Qt.ArrowCursor)
        
        if direction:
            self.logger.debug(f"Cursor updated for direction: {direction}")

    def handle_mouse_press(self, event):
        """Handle mouse press for dragging and resizing."""
        if event.button() == Qt.LeftButton:
            self.resize_direction = self.get_resize_direction(event.pos())
            
            if self.resize_direction:
                # Starting resize
                self.logger.debug(f"Starting resize in direction: {self.resize_direction}")
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.main_window.geometry()
                self.logger.debug(f"Resize start geometry: {self.resize_start_geometry}")
            else:
                # Starting drag
                self.logger.debug("Starting window drag")
                self.drag_position = event.globalPos() - self.main_window.frameGeometry().topLeft()
            
            event.accept()

    def handle_mouse_move(self, event):
        """Handle mouse move for dragging and resizing."""
        if event.buttons() == Qt.LeftButton:
            if self.resize_direction and hasattr(self, 'resize_start_pos'):
                # Handle resizing
                self.handle_resize(event.globalPos())
            elif hasattr(self, 'drag_position'):
                # Handle dragging
                new_pos = event.globalPos() - self.drag_position
                self.main_window.move(new_pos)
                self.logger.debug(f"Window dragged to: ({new_pos.x()}, {new_pos.y()})")
                self.position_save_timer.stop()
                self.position_save_timer.start(500)
            
            event.accept()
        else:
            # Update cursor when hovering
            direction = self.get_resize_direction(event.pos())
            self.update_cursor(direction)

    def handle_resize(self, global_pos):
        """Handle window resizing based on direction."""
        if not self.resize_start_pos or not self.resize_start_geometry:
            self.logger.debug("No resize start position or geometry, skipping resize")
            return
        
        delta = global_pos - self.resize_start_pos
        start_geo = self.resize_start_geometry
        
        new_x = start_geo.x()
        new_y = start_geo.y()
        new_width = start_geo.width()
        new_height = start_geo.height()
        
        # Apply minimum size constraints
        min_size = self.main_window.minimumSize()
        
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
        self.main_window.setGeometry(new_x, new_y, new_width, new_height)
        self.logger.debug(f"Window resized to: ({new_x}, {new_y}) {new_width}x{new_height}")
        
        # Reposition copy button if visible
        if hasattr(self.main_window, 'copy_button') and self.main_window.copy_button.isVisible():
            if hasattr(self.main_window, 'position_copy_button'):
                self.main_window.position_copy_button()
                self.logger.debug("Copy button repositioned after resize")

    def handle_mouse_release(self, event):
        """Clean up after mouse release."""
        if event.button() == Qt.LeftButton:
            if self.resize_direction:
                self.logger.debug(f"Finished resizing in direction: {self.resize_direction}")
            else:
                self.logger.debug("Finished dragging window")
                
            self.resize_direction = None
            self.resize_start_pos = None
            self.resize_start_geometry = None
            self.main_window.setCursor(Qt.ArrowCursor)
            event.accept()

    def handle_leave_event(self, event):
        """Reset cursor when mouse leaves window."""
        if not self.resize_direction:  # Only reset if not currently resizing
            self.main_window.setCursor(Qt.ArrowCursor)
            self.logger.debug("Mouse left window, cursor reset to arrow")

    def handle_move_event(self, event):
        """Handle window move events."""
        # Debounce position saving for any move event
        if hasattr(self, 'position_save_timer'):
            self.position_save_timer.stop()
            self.position_save_timer.start(500)
            self.logger.debug("Position save timer restarted (500ms debounce)")

    def handle_close_event(self, event):
        """Handle close event - hide to tray or quit."""
        self.logger.debug("Close event triggered")
        
        if not self.should_quit and hasattr(self.main_window, 'tray_manager'):
            if hasattr(self.main_window.tray_manager, 'tray_icon') and self.main_window.tray_manager.tray_icon.isVisible():
                self.logger.info("Hiding to tray instead of quitting")
                event.ignore()
                self.hide_window()
                return
        
        self.logger.info("Actually quitting application")
        if hasattr(self.main_window, 'hotkey_manager'):
            self.logger.debug("Cleaning up hotkey manager")
            self.main_window.hotkey_manager.cleanup()
        event.accept()

    def animate_resize(self, width, height, fast=False):
        """Delegate to animation manager if available."""
        self.logger.debug(f"Animating resize to {width}x{height}, fast={fast}")
        
        if hasattr(self.main_window, 'animation_manager'):
            self.main_window.animation_manager.animate_window_resize(self.main_window, width, height, fast)
        else:
            # Fallback to immediate resize
            self.logger.debug("No animation manager, using immediate resize")
            self.main_window.resize(width, height)

    def restore_geometry(self):
        """Restore window position from config."""
        try:
            x = self.config.get('position_x', 100)
            y = self.config.get('position_y', 100)
            
            self.logger.debug(f"Restoring geometry from config: ({x}, {y})")
            
            # Validate position is on screen
            screen = QApplication.primaryScreen().geometry()
            if x < 0 or y < 0 or x > screen.width() - 100 or y > screen.height() - 100:
                self.logger.debug(f"Position ({x}, {y}) is off-screen, using default (100, 100)")
                x, y = 100, 100
            
            self.main_window.move(x, y)
            self.logger.debug(f"Restored window position to ({x}, {y})")
            
        except Exception as e:
            self.logger.error(f"Error restoring geometry: {e}")
            self.main_window.move(100, 100)

    def save_geometry(self):
        """Save window position to config."""
        try:
            pos = self.main_window.pos()
            self.config.set('position_x', pos.x())
            self.config.set('position_y', pos.y())
            self.logger.debug(f"Saved window position: ({pos.x()}, {pos.y()})")
            
        except Exception as e:
            self.logger.error(f"Error saving geometry: {e}")