from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence
import logging

from managers.style_manager import StyleManager
from utils.constants import Text, Theme


class HotkeyRecorderDialog(QDialog):
    """Dialog for recording hotkey combinations."""
    
    hotkey_recorded = pyqtSignal(str)  # Emits the recorded hotkey string
    
    def __init__(self, parent=None, current_hotkey="", title="Record Hotkey", config=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.style_manager = StyleManager(self.logger)
        self.config = config

        self.current_hotkey = current_hotkey
        self.recorded_keys = set()
        self.recorded_hotkey = ""
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        self.setup_ui()
        self.apply_styles()

        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel(Text.HOTKEY_DIALOG_TITLE)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Current hotkey display
        if self.current_hotkey:
            current_label = QLabel(f"Current: {self.current_hotkey}")
            current_label.setAlignment(Qt.AlignCenter)
            current_label.setObjectName("current_label")
            layout.addWidget(current_label)
        
        # Recorded hotkey display
        self.hotkey_display = QLabel(Text.HOTKEY_DIALOG_HOTKEY_DISPLAY)
        self.hotkey_display.setAlignment(Qt.AlignCenter)
        self.hotkey_display.setObjectName("hotkey_display")
        layout.addWidget(self.hotkey_display)
        
        # Instructions
        instructions = QLabel(Text.HOTKEY_DIALOG_INSTRUCTIONS)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setObjectName("instructions")
        layout.addWidget(instructions)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_hotkey)
        self.save_button.setEnabled(False)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_keys)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Set focus to capture key events
        self.setFocusPolicy(Qt.StrongFocus)

    def apply_styles(self):
        self.logger.debug("Applying styles to hotkey recorder")
        if self.config:
            current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
            self.style_manager.set_theme(current_theme)
        
        dialog_styles = self.style_manager.get_hotkey_recorder_style()
        self.setStyleSheet(dialog_styles)
        
    def keyPressEvent(self, event):
        """Handle key press events to record hotkey combination."""
        key = event.key()
        
        # Ignore certain keys
        if key in (Qt.Key_unknown, Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape):
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                if self.save_button.isEnabled():
                    self.save_hotkey()
            elif key == Qt.Key_Escape:
                self.reject()
            return
            
        # Add key to recorded set
        self.recorded_keys.add(key)
        self.update_display()
        
    def keyReleaseEvent(self, event):
        """Handle key release events."""
        # Don't remove keys on release - user might want to hold multiple keys
        pass
        
    def update_display(self):
        """Update the hotkey display with current key combination."""
        if not self.recorded_keys:
            self.hotkey_display.setText("Press keys...")
            self.save_button.setEnabled(False)
            return
            
        # Convert keys to readable format
        key_names = []
        modifiers = []
        regular_keys = []
        
        for key in self.recorded_keys:
            key_name = self.key_to_string(key)
            if key in (Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta):
                modifiers.append(key_name)
            else:
                regular_keys.append(key_name)
        
        # Build hotkey string (modifiers first, then regular keys)
        all_keys = sorted(modifiers) + sorted(regular_keys)
        hotkey_string = "+".join(all_keys)
        
        self.hotkey_display.setText(hotkey_string)
        self.recorded_hotkey = hotkey_string.lower()  # Store in pynput format
        self.save_button.setEnabled(len(all_keys) > 0)
        
    def key_to_string(self, key):
        """Convert Qt key code to readable string."""
        key_map = {
            Qt.Key_Control: "<ctrl>",
            Qt.Key_Alt: "<alt>", 
            Qt.Key_Shift: "<shift>",
            Qt.Key_Meta: "<cmd>",  # Windows key / Cmd key
            Qt.Key_Space: "<space>",
            Qt.Key_Tab: "<tab>",
            Qt.Key_Backspace: "<backspace>",
            Qt.Key_Delete: "<delete>",
            Qt.Key_Insert: "<insert>",
            Qt.Key_Home: "<home>",
            Qt.Key_End: "<end>",
            Qt.Key_PageUp: "<page_up>",
            Qt.Key_PageDown: "<page_down>",
            Qt.Key_Up: "<up>",
            Qt.Key_Down: "<down>",
            Qt.Key_Left: "<left>",
            Qt.Key_Right: "<right>",
        }
        
        if key in key_map:
            return key_map[key]
        elif Qt.Key_F1 <= key <= Qt.Key_F35:
            return f"f{key - Qt.Key_F1 + 1}"
        elif key < 256:
            # Regular character keys
            char = chr(key).lower()
            return char
        else:
            return f"key_{key}"
            
    def clear_keys(self):
        """Clear all recorded keys."""
        self.recorded_keys.clear()
        self.recorded_hotkey = ""
        self.update_display()
        
    def save_hotkey(self):
        """Save the recorded hotkey and close dialog."""
        if self.recorded_hotkey:
            self.logger.info(f"Hotkey recorded: {self.recorded_hotkey}")
            self.hotkey_recorded.emit(self.recorded_hotkey)
            self.accept()
        else:
            self.logger.warning("No hotkey recorded")
            
    def get_recorded_hotkey(self):
        """Get the recorded hotkey string."""
        return self.recorded_hotkey


# Example usage function
def show_hotkey_recorder(parent=None, current_hotkey="", title="Record Hotkey"):
    """Show hotkey recorder dialog and return the recorded hotkey."""
    dialog = HotkeyRecorderDialog(parent, current_hotkey, title)
    
    recorded_hotkey = None
    def on_hotkey_recorded(hotkey):
        nonlocal recorded_hotkey
        recorded_hotkey = hotkey
    
    dialog.hotkey_recorded.connect(on_hotkey_recorded)
    
    if dialog.exec_() == QDialog.Accepted:
        return recorded_hotkey
    return None