from PyQt5.QtCore import QObject, pyqtSignal, QRect, QPropertyAnimation, QEasingCurve, QPoint
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
        self._is_dragging = False
        self._is_resizing = False
        self._drag_start = None
        self._resize_start = None
        self._resize_edge = None
        
        # Resize detection margins
        self._resize_margin = 10
        
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
            
    def _get_resize_edge(self, pos):
        """Determine which edge is being resized"""
        if not self._window:
            return None
            
        rect = self._window.rect()
        margin = self._resize_margin
        
        left = pos.x() <= margin
        right = pos.x() >= rect.width() - margin
        top = pos.y() <= margin
        bottom = pos.y() >= rect.height() - margin
        
        if left and top:
            return 'top-left'
        elif right and top:
            return 'top-right'
        elif left and bottom:
            return 'bottom-left'
        elif right and bottom:
            return 'bottom-right'
        elif left:
            return 'left'
        elif right:
            return 'right'
        elif top:
            return 'top'
        elif bottom:
            return 'bottom'
        return None

    def quit_application(self):
        """Quit application cleanly"""
        self.logger.info("WindowManager: Quitting application")
        if self._window:
            self.save_geometry()
        QApplication.quit()


    def _set_cursor_for_edge(self, edge):
        """Set appropriate cursor for resize edge"""
        if not self._window:
            return
            
        cursor_map = {
            'top-left': Qt.SizeFDiagCursor,
            'top-right': Qt.SizeBDiagCursor,
            'bottom-left': Qt.SizeBDiagCursor,
            'bottom-right': Qt.SizeFDiagCursor,
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
        }
        
        if edge in cursor_map:
            self._window.setCursor(cursor_map[edge])
        else:
            self._window.setCursor(Qt.ArrowCursor)
            
    # Mouse event handlers - self-contained
    def handle_mouse_press(self, event):
        """Handle mouse press for dragging/resizing"""
        if not self._window:
            return
            
        self._drag_start = event.globalPos()
        self._resize_edge = self._get_resize_edge(event.pos())
        
        if self._resize_edge:
            self._is_resizing = True
            self._resize_start = self._window.geometry()
            self.logger.debug(f"WindowManager: Starting resize from edge: {self._resize_edge}")
        else:
            self._is_dragging = True
            self.logger.debug("WindowManager: Starting window drag")
            
    def handle_mouse_move(self, event):
        """Handle mouse move for dragging/resizing"""
        if not self._window:
            return
            
        if self._is_resizing and self._drag_start and self._resize_start:
            self._handle_resize(event)
        elif self._is_dragging and self._drag_start:
            self._handle_drag(event)
        else:
            # Update cursor based on position
            edge = self._get_resize_edge(event.pos())
            self._set_cursor_for_edge(edge)
            
    def _handle_drag(self, event):
        """Handle window dragging"""
        delta = event.globalPos() - self._drag_start
        new_pos = self._window.pos() + delta
        self._window.move(new_pos)
        self._drag_start = event.globalPos()
        
    def _handle_resize(self, event):
        """Handle window resizing"""
        delta = event.globalPos() - self._drag_start
        original_geo = self._resize_start
        
        new_x = original_geo.x()
        new_y = original_geo.y()
        new_width = original_geo.width()
        new_height = original_geo.height()
        
        # Calculate new geometry based on resize edge
        if 'left' in self._resize_edge:
            new_x = original_geo.x() + delta.x()
            new_width = original_geo.width() - delta.x()
        elif 'right' in self._resize_edge:
            new_width = original_geo.width() + delta.x()
            
        if 'top' in self._resize_edge:
            new_y = original_geo.y() + delta.y()
            new_height = original_geo.height() - delta.y()
        elif 'bottom' in self._resize_edge:
            new_height = original_geo.height() + delta.y()
            
        # Apply minimum size constraints
        min_width = 300
        min_height = 100
        
        if new_width < min_width:
            if 'left' in self._resize_edge:
                new_x = original_geo.x() + original_geo.width() - min_width
            new_width = min_width
            
        if new_height < min_height:
            if 'top' in self._resize_edge:
                new_y = original_geo.y() + original_geo.height() - min_height
            new_height = min_height
            
        self._window.setGeometry(new_x, new_y, new_width, new_height)
        
    def handle_mouse_release(self, event):
        """Handle mouse release"""
        if self._is_dragging:
            self.logger.debug("WindowManager: Drag completed")
        elif self._is_resizing:
            self.logger.debug("WindowManager: Resize completed")
            
        self._is_dragging = False
        self._is_resizing = False
        self._drag_start = None
        self._resize_start = None
        self._resize_edge = None
        
    def handle_close_event(self, event):
        """Handle close event - hide instead of quit"""
        self.logger.debug("WindowManager: Close event - hiding to tray")
        event.ignore()
        self.hide_window()
        
    def handle_leave_event(self, event):
        """Reset cursor on leave"""
        if self._window:
            self._window.setCursor(Qt.ArrowCursor)
            
    def handle_move_event(self, event):
        """Handle window move event"""
        # Save geometry when window is moved
        if self._window and not self._is_dragging:
            self.save_geometry()

    # def restore_geometry(self):
    #     """Restore geometry from config"""
    #     saved_geo = self.config.get('window_geometry')
    #     if saved_geo and self._window:
    #         try:
    #             self._window.setGeometry(
    #                 saved_geo['x'], saved_geo['y'],
    #                 saved_geo['width'], saved_geo['height']
    #             )
    #             self.logger.debug(f"WindowManager: Geometry restored: {saved_geo}")
    #         except (KeyError, TypeError) as e:
    #             self.logger.error(f"WindowManager: Error restoring geometry: {e}")
    #     else:
    #         self.logger.debug("WindowManager: No saved geometry found")

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
        geometry = self._window.geometry()
        geometry_data = {
            'x': geometry.x(),
            'y': geometry.y(),
            'width': geometry.width(),
            'height': geometry.height()
        }

        try:
            pos = self._window.pos()
            self.config.set('position_x', geometry_data['x'])
            self.config.set('position_y', geometry_data['y'])
            self.logger.debug(f"Saved window position: ({geometry_data['x']}, {geometry_data['y']})")
            
        except Exception as e:
            self.logger.error(f"Error saving geometry: {e}")