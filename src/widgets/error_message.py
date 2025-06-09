import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QPropertyAnimation, QEasingCurve
from managers.style_manager import StyleManager
from utils.constants import (
    ElementSize, Files, InputSettings, Text, WindowSize)


class ErrorMessage(QWidget):
    """Floating error message widget that auto-hides after a timeout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("errorMessage")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        # Create layout and label
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)

        # Timer for auto-hide
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_with_animation)


        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(
            self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.finished.connect(self._on_animation_finished)

        self.is_hiding = False

    def show_message(self, message, duration=5000):
        """Show error message for specified duration (in milliseconds)."""
        self.message_label.setText(message)
        self.adjustSize()  # Resize to fit content

        # Reset opacity and show
        self.opacity_effect.setOpacity(1.0)
        self.show()
        self.raise_()

        # Start hide timer
        self.hide_timer.start(duration)
        self.is_hiding = False

    def hide_with_animation(self):
        """Hide the message with fade animation."""
        if self.is_hiding:
            return

        self.is_hiding = True
        self.hide_timer.stop()

        # Animate fade out
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

    def _on_animation_finished(self):
        """Called when fade animation completes."""
        if self.is_hiding:
            self.hide()
            self.is_hiding = False

    def mousePressEvent(self, event):
        """Allow clicking to dismiss the message."""
        self.hide_with_animation()
        super().mousePressEvent(event)
