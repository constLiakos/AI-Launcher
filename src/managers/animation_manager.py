import logging
from PyQt5.QtCore import QTimer, QPropertyAnimation, QRect, QEasingCurve, QObject, QVariantAnimation
from PyQt5.QtGui import QColor
from managers.styles import StyleManager
from utils.constants import AnimationConfig, ElementSize, Timing

class AnimationManager(QObject):
    """Manages all animations for the application."""
    
    def __init__(self, parent_widget, logger:logging.Logger, style_manager:StyleManager):
        super().__init__(parent_widget)
        self.logger = logger.getChild('animation_manager')
        self.parent = parent_widget
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self.update_thinking_animation)
        self.thinking_phase = 0
        self.thinking_colors = [
            QColor(79, 156, 249, 204),   # Blue
            QColor(139, 92, 246, 204),   # Purple
            QColor(236, 72, 153, 204),   # Pink
            QColor(79, 156, 249, 204),   # Blue
            QColor(34, 197, 94, 204),    # Green
            QColor(249, 115, 22, 204)    # Orange
        ]
        self.active_animations = {}
        self.current_thinking_color = self.thinking_colors[0]
        self.input_field = None  # Initialize as None
        self.style_manager:StyleManager = style_manager
            
    
    def start_thinking_animation(self, input_field):
        """Start animated thinking effect on input border."""
        self.input_field = input_field
        self.thinking_phase = 0
        self.thinking_timer.start(AnimationConfig.THINKING_UPDATE_INTERVAL)
        
    def stop_thinking_animation(self):
        """Stop thinking animation."""
        self.thinking_timer.stop()
        if 'thinking_color' in self.active_animations:
            self.active_animations['thinking_color'].stop()
            del self.active_animations['thinking_color']
    
    def update_thinking_animation(self):
        """Update thinking animation colors with smooth transitions."""
        if not hasattr(self, 'input_field'):
            return
        
        # Calculate next color
        next_phase = (self.thinking_phase + 1) % len(self.thinking_colors)
        current_color = self.thinking_colors[self.thinking_phase]
        next_color = self.thinking_colors[next_phase]
        
        # Stop any existing smooth transition
        if 'thinking_color' in self.active_animations:
            self.active_animations['thinking_color'].stop()
        
        # Create smooth transition to next color
        color_animation = QVariantAnimation(self)
        color_animation.setDuration(200)  # Match your original timer interval
        color_animation.setEasingCurve(QEasingCurve.InOutQuad)
        color_animation.setStartValue(current_color)
        color_animation.setEndValue(next_color)
        
        color_animation.valueChanged.connect(
            lambda color: self._apply_smooth_color(color)
        )
        color_animation.finished.connect(
            lambda: self._on_smooth_transition_finished(next_phase)
        )
        
        self.active_animations['thinking_color'] = color_animation
        color_animation.start()

    def _on_smooth_transition_finished(self, next_phase):
        """Update phase when smooth transition completes."""
        self.thinking_phase = next_phase
        if 'thinking_color' in self.active_animations:
            del self.active_animations['thinking_color']

    def _apply_smooth_color(self, color):
        """Apply the interpolated color during smooth transition."""
        if hasattr(self, 'input_field'):
            color_str = f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()/255:.1f})"
            style = self.style_manager.get_animated_thinking_style(color_str)
            self.input_field.setStyleSheet(style)

    def _stop_animation(self, animation_key):
        """Stop existing animation if running."""
        if animation_key in self.active_animations:
            animation = self.active_animations[animation_key]
            if animation.state() == QPropertyAnimation.Running:
                animation.stop()
            del self.active_animations[animation_key]
    
    def animate_resize(self, widget, width, height, fast=False):
        """Unified resize animation method using constants."""
        animation_key = f"resize_{id(widget)}"
        self._stop_animation(animation_key)
        
        # Choose animation parameters based on speed using constants
        duration = AnimationConfig.RESIZE_FAST_DURATION if fast else AnimationConfig.RESIZE_DURATION
        easing = AnimationConfig.RESIZE_FAST_EASING if fast else AnimationConfig.RESIZE_EASING
        
        # Disable updates during animation for smoother performance
        if AnimationConfig.DISABLE_UPDATES_DURING_RESIZE:
            widget.setUpdatesEnabled(False)
        
        # Create and configure animation
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        
        # Calculate geometry - keep top-left position, only expand size
        current_geometry = widget.geometry()
        new_geometry = QRect(
            current_geometry.x(),
            current_geometry.y(),
            width,
            height
        )
        
        animation.setStartValue(current_geometry)
        animation.setEndValue(new_geometry)
        
        # Store animation and setup completion callback
        self.active_animations[animation_key] = animation
        animation.finished.connect(lambda: self._finalize_resize(widget, width, height, animation_key))
        animation.start()
    
    def _finalize_resize(self, widget, width, height, animation_key):
        """Finalize resize operation and cleanup using constants."""
        # Clean up animation reference
        if animation_key in self.active_animations:
            del self.active_animations[animation_key]
        
        # Re-enable updates and set final size
        if AnimationConfig.DISABLE_UPDATES_DURING_RESIZE:
            widget.setUpdatesEnabled(True)
        widget.setFixedSize(width, height)
        
        # Handle response area height adjustment if this is the main window
        if hasattr(widget, 'response_area'):
            min_height = ElementSize.RESPONSE_MIN_HEIGHT
            max_height = ElementSize.RESPONSE_MAX_HEIGHT
            available_height = height - ElementSize.RESPONSE_MARGIN_BOTTOM
            
            # Calculate optimal height
            optimal_height = max(min_height, min(max_height, available_height))
            
            # Actually set the height, not just the maximum
            widget.response_area.setFixedHeight(optimal_height)
        
        widget.update()
    
