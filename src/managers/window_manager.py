from PyQt5.QtCore import QObject, pyqtSignal, QRect, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

class WindowManager(QObject):
    # Signals for communication (no direct parent calls)
    tray_message_requested = pyqtSignal(str, str)  # title, message
    geometry_saved = pyqtSignal(QRect)  # when geometry is saved
    window_minimized = pyqtSignal()
    window_restored = pyqtSignal()
    
    def __init__(self, logger, config):
        super().__init__()
        self.logger = logger
        self.config = config
        self._window = None
        self._animation = None
        self._was_minimized = False

        # Window state tracking
        self.resize_direction = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.drag_position = None
        
        # Resize detection margins
        self._resize_margin_horizontal = 10
        self._resize_margin_vertical = 10
        
        # Position save timer to debounce position saving
        self.position_save_timer = QTimer()
        self.position_save_timer.setSingleShot(True)
        self.position_save_timer.timeout.connect(self.save_geometry)
        
    def set_window(self, window):
        """Set the window to manage - called after window creation"""
        self._window = window
        self.logger.debug("WindowManager: Window reference set")
        
    def setup_window_properties(self):
        """Setup window properties - self-contained"""
        if not self._window:
            self.logger.warning("WindowManager: No window set for setup")
            return
            
        self.logger.debug("WindowManager: Setting up window properties")
        
        # Set window flags
        self._window.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        
        # Set attributes
        self._window.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set minimum size
        self._window.setMinimumSize(300, 100)
        
        # Restore saved geometry
        self.restore_geometry()
        
        self.logger.debug("WindowManager: Window properties setup complete")
        
    def show_window(self):
        """Show window - direct control, emit signal for notifications"""
        if self._window:
            # Check if we're restoring from minimized state
            was_minimized = self._was_minimized
            
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()
            self._was_minimized = False
            
            # Emit signal if we were minimized
            if was_minimized:
                self.window_restored.emit()
                
            self.logger.debug("WindowManager: Window shown and activated")
        else:
            self.logger.warning("WindowManager: Cannot show window - no window reference")
            
    def hide_window(self):
        """Hide window and notify via signal"""
        if self._window:
            self.save_geometry()
            self._window.hide()
            self._was_minimized = True  # Mark as minimized
            self.window_minimized.emit()  # Emit minimize signal
            self.logger.debug("WindowManager: Window hidden/minimized")
            # Signal for any additional actions (like tray notification)
            self.tray_message_requested.emit("AI Launcher", "Hidden to system tray")
        else:
            self.logger.warning("WindowManager: Cannot hide window - no window reference")
        
    def animate_resize(self, width, height, fast=False):
        """Self-contained animation"""
        if not self._window:
            self.logger.warning("WindowManager: Cannot animate resize - no window reference")
            return
            
        self.logger.debug(f"WindowManager: Animating resize to {width}x{height}")
        
        # Clean up previous animation
        if self._animation and self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()
            
        duration = 100 if fast else 200
        self._animation = QPropertyAnimation(self._window, b"geometry")
        self._animation.setDuration(duration)
        
        current_geo = self._window.geometry()
        target_geo = QRect(current_geo.x(), current_geo.y(), width, height)
        
        self._animation.setStartValue(current_geo)
        self._animation.setEndValue(target_geo)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.start()
            
    def get_resize_direction(self, pos):
        """Determine resize direction based on mouse position - left, right, bottom only"""
        if not self._window:
            return None
            
        rect = self._window.rect()
        left = pos.x() <= self._resize_margin_horizontal
        right = pos.x() >= rect.width() - self._resize_margin_horizontal
        bottom = pos.y() >= rect.height() - self._resize_margin_vertical
        
        direction = None
        if bottom and left:
            direction = "bottom-left"
        elif bottom and right:
            direction = "bottom-right"
        elif left:
            direction = "left"
        elif right:
            direction = "right"
        elif bottom:
            direction = "bottom"
            
        if direction:
            self.logger.debug(f"Resize direction detected: {direction} at pos ({pos.x()}, {pos.y()})")
        return direction

    def update_cursor(self, direction):
        """Update cursor based on resize direction"""
        if not self._window:
            return
            
        if direction == "bottom-left":
            self._window.setCursor(Qt.SizeBDiagCursor)
        elif direction == "bottom-right":
            self._window.setCursor(Qt.SizeFDiagCursor)
        elif direction == "left" or direction == "right":
            self._window.setCursor(Qt.SizeHorCursor)
        elif direction == "bottom":
            self._window.setCursor(Qt.SizeVerCursor)
        else:
            self._window.setCursor(Qt.ArrowCursor)
            
        if direction:
            self.logger.debug(f"Cursor updated for direction: {direction}")

    def quit_application(self):
        """Quit application cleanly"""
        self.logger.info("WindowManager: Quitting application")
        if self._window:
            self.save_geometry()
        QApplication.quit()

    # Mouse event handlers - modified for new behavior
    def handle_mouse_press(self, event):
        """Handle mouse press for dragging/resizing"""
        if not self._window:
            return
            
        if event.button() == Qt.LeftButton:
            self.resize_direction = self.get_resize_direction(event.pos())
            
            if self.resize_direction:
                # Starting resize
                self.logger.debug(f"Starting resize in direction: {self.resize_direction}")
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self._window.geometry()
            else:
                # Starting drag (top area or anywhere without resize direction)
                self.logger.debug("Starting window drag")
                self.drag_position = event.globalPos() - self._window.frameGeometry().topLeft()
            
            event.accept()
            
    def handle_mouse_move(self, event):
        """Handle mouse move for dragging/resizing"""
        if not self._window:
            return
            
        if event.buttons() == Qt.LeftButton:
            if self.resize_direction and self.resize_start_pos:
                # Handle resizing
                self.handle_resize(event.globalPos())
            elif hasattr(self, 'drag_position') and self.drag_position is not None:
                # Handle dragging
                new_pos = event.globalPos() - self.drag_position
                self._window.move(new_pos)
                self.logger.debug(f"Window dragged to: ({new_pos.x()}, {new_pos.y()})")
                # Debounce position saving
                self.position_save_timer.stop()
                self.position_save_timer.start(500)
            event.accept()
        else:
            # Update cursor when hovering
            direction = self.get_resize_direction(event.pos())
            self.update_cursor(direction)
            
    def handle_resize(self, global_pos):
        """Handle window resizing based on direction"""
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
        min_size = self._window.minimumSize()
        
        # Calculate new geometry based on resize direction
        if "left" in self.resize_direction:
            new_width = max(min_size.width(), start_geo.width() - delta.x())
            new_x = start_geo.x() + start_geo.width() - new_width
        elif "right" in self.resize_direction:
            new_width = max(min_size.width(), start_geo.width() + delta.x())
            
        if "bottom" in self.resize_direction:
            new_height = max(min_size.height(), start_geo.height() + delta.y())
            
        # Apply the new geometry
        self._window.setGeometry(new_x, new_y, new_width, new_height)

        self.logger.debug(f"Window resized to: ({new_x}, {new_y}) {new_width}x{new_height}")
        
    def handle_mouse_release(self, event):
        """Clean up after mouse release"""
        if event.button() == Qt.LeftButton:
            if self.resize_direction:
                self.logger.debug(f"Finished resizing in direction: {self.resize_direction}")
            else:
                self.logger.debug("Finished dragging window")
                
            # Clean up state
            self.resize_direction = None
            self.resize_start_pos = None
            self.resize_start_geometry = None
            self.drag_position = None
            self._window.setCursor(Qt.ArrowCursor)
            event.accept()
        
    def handle_close_event(self, event):
        """Handle close event - hide instead of quit"""
        self.logger.debug("WindowManager: Close event - hiding to tray")
        event.ignore()
        self.hide_window()
        
    def handle_leave_event(self, event):
        """Reset cursor when mouse leaves window"""
        if self._window and not self.resize_direction:  # Only reset if not currently resizing
            self._window.setCursor(Qt.ArrowCursor)
            self.logger.debug("Mouse left window, cursor reset to arrow")
            
    def handle_move_event(self, event):
        """Handle window move events"""
        # Debounce position saving for any move event
        if hasattr(self, 'position_save_timer'):
            self.position_save_timer.stop()
            self.position_save_timer.start(2000)
            self.logger.debug("Position save timer restarted (2sec debounce)")

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
            
            self._window.move(x, y)
            self.logger.debug(f"Restored window position to ({x}, {y})")
            
        except Exception as e:
            self.logger.error(f"Error restoring geometry: {e}")
            self._window.move(100, 100)

    def save_geometry(self):
        """Save window position to config."""
        if not self._window:
            return
            
        try:
            pos = self._window.pos()
            self.config.set('position_x', pos.x())
            self.config.set('position_y', pos.y())
            self.logger.debug(f"Saved window position: ({pos.x()}, {pos.y()})")
            
        except Exception as e:
            self.logger.error(f"Error saving geometry: {e}")