import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QKeySequence, QIcon
from utils.constants import WindowSize, ElementSize, Timing, Text

logger = logging.getLogger(__name__)

class WindowManager:
    def __init__(self, main_window, config, logger_instance):
        self.main_window = main_window
        self.config = config
        self.logger = logger_instance
        
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

    def setup_window_properties(self):
        """Set up basic window properties."""
        self.main_window.setWindowTitle("AI Assistant")
        self.main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.main_window.setAttribute(Qt.WA_TranslucentBackground)
        self.main_window.setMinimumSize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)
        self.main_window.resize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT)

    def show_window(self):
        """Show and raise the window to front."""
        try:
            # Check if we should clear previous response when reopening
            if self.config.get('clear_last_response_on_minimize', False):
                self.logger.debug("Clearing previous response on window show")
                self._clear_response_on_show()

            self.logger.debug(f"Window shown, position: ({self.main_window.x()}, {self.main_window.y()})")
            
            # Ensure window is visible
            if self.main_window.isMinimized():
                self.main_window.setWindowState(self.main_window.windowState() & ~Qt.WindowMinimized)
            
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Focus on input field
            if hasattr(self.main_window, 'input_field'):
                self.main_window.input_field.setFocus()
                
        except Exception as e:
            self.logger.error(f"Error showing window: {e}")
            # Fallback
            self.main_window.show()
            if hasattr(self.main_window, 'input_field'):
                self.main_window.input_field.setFocus()

    def hide_window(self):
        """Hide the window to system tray."""
        self.main_window.hide()
        
        # Show tray message if tray is available
        if hasattr(self.main_window, 'tray_manager') and hasattr(self.main_window.tray_manager, 'tray_icon'):
            self.main_window.tray_manager.show_background_message()
        
        # Clear history if configured
        clear_history_on_minimize = self.config.get('clear_history_on_minimize', False)
        if clear_history_on_minimize and hasattr(self.main_window, 'conversation_manager'):
            self.main_window.conversation_manager.clear_history()

    def _clear_response_on_show(self):
        """Clear response and reset window when showing."""
        if hasattr(self.main_window, 'response_area'):
            self.main_window.response_area.setHtml("")
            self.main_window.response_area.setVisible(False)
        
        if hasattr(self.main_window, 'copy_button'):
            self.main_window.copy_button.setVisible(False)
        
        # Reset to compact size
        if hasattr(self.main_window, 'animate_resize'):
            self.main_window.animate_resize(WindowSize.COMPACT_WIDTH, WindowSize.COMPACT_HEIGHT, fast=True)
        
        # Clear state manager response
        if hasattr(self.main_window, 'state_manager'):
            if hasattr(self.main_window.state_manager, 'accumulated_response'):
                self.main_window.state_manager.accumulated_response = ""
        
        # Clear input and conversation
        if hasattr(self.main_window, 'input_field'):
            self.main_window.input_field.clear()
        
        if hasattr(self.main_window, 'conversation_manager'):
            self.main_window.conversation_manager.clear_history()

    def quit_application(self):
        """Properly quit the application."""
        self.should_quit = True
        if hasattr(self.main_window, 'tray_manager') and hasattr(self.main_window.tray_manager, 'tray_icon'):
            self.main_window.tray_manager.tray_icon.hide()
        QApplication.quit()

    def get_resize_direction(self, pos):
        """Determine resize direction based on mouse position."""
        rect = self.main_window.rect()

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
            self.main_window.setCursor(Qt.SizeFDiagCursor)
        elif direction == "top-right" or direction == "bottom-left":
            self.main_window.setCursor(Qt.SizeBDiagCursor)
        elif direction == "left" or direction == "right":
            self.main_window.setCursor(Qt.SizeHorCursor)
        elif direction == "top" or direction == "bottom":
            self.main_window.setCursor(Qt.SizeVerCursor)
        else:
            self.main_window.setCursor(Qt.ArrowCursor)

    def handle_mouse_press(self, event):
        """Handle mouse press for dragging and resizing."""
        if event.button() == Qt.LeftButton:
            self.resize_direction = self.get_resize_direction(event.pos())
            
            if self.resize_direction:
                # Starting resize
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.main_window.geometry()
            else:
                # Starting drag
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
                self.main_window.move(event.globalPos() - self.drag_position)
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
        
        # Reposition copy button if visible
        if hasattr(self.main_window, 'copy_button') and self.main_window.copy_button.isVisible():
            if hasattr(self.main_window, 'position_copy_button'):
                self.main_window.position_copy_button()

    def handle_mouse_release(self, event):
        """Clean up after mouse release."""
        if event.button() == Qt.LeftButton:
            self.resize_direction = None
            self.resize_start_pos = None
            self.resize_start_geometry = None
            self.main_window.setCursor(Qt.ArrowCursor)
            event.accept()

    def handle_leave_event(self, event):
        """Reset cursor when mouse leaves window."""
        if not self.resize_direction:  # Only reset if not currently resizing
            self.main_window.setCursor(Qt.ArrowCursor)

    def handle_move_event(self, event):
        """Handle window move events."""
        # Debounce position saving for any move event
        if hasattr(self, 'position_save_timer'):
            self.position_save_timer.stop()
            self.position_save_timer.start(500)

    def handle_close_event(self, event):
        """Handle close event - hide to tray or quit."""
        self.logger.debug("Close event triggered")
        
        if not self.should_quit and hasattr(self.main_window, 'tray_manager'):
            if hasattr(self.main_window.tray_manager, 'tray_icon') and self.main_window.tray_manager.tray_icon.isVisible():
                self.logger.debug("Hiding to tray instead of quitting")
                event.ignore()
                self.hide_window()
                return
        
        self.logger.debug("Actually quitting application")
        if hasattr(self.main_window, 'hotkey_manager'):
            self.main_window.hotkey_manager.cleanup()
        event.accept()

    def animate_resize(self, width, height, fast=False):
        """Delegate to animation manager if available."""
        if hasattr(self.main_window, 'animation_manager'):
            self.main_window.animation_manager.animate_window_resize(self.main_window, width, height, fast)
        else:
            # Fallback to immediate resize
            self.main_window.resize(width, height)


    def restore_geometry(self):
        """Restore window position from config."""
        try:
            x = self.config.get('position_x', 100)
            y = self.config.get('position_y', 100)
            
            # Validate position is on screen
            screen = QApplication.primaryScreen().geometry()
            if x < 0 or y < 0 or x > screen.width() - 100 or y > screen.height() - 100:
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


    # def save_geometry(self):
    #     """Save window position."""
    #     self.config.set('position_x', self.parent.x())
    #     self.config.set('position_y', self.parent.y())
    #     self.logger.debug(f"Position saved: ({self.parent.x()}, {self.parent.y()})")
    
    # def restore_geometry(self):
    #     """Restore window position."""
    #     x = self.config.get('position_x', WindowSize.DEFAULT_X)
    #     y = self.config.get('position_y', WindowSize.DEFAULT_Y)
    #     self.logger.debug(f"Restoring window position to ({x}, {y})")
    #     self.parent.move(x, y)