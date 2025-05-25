from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QFrame, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
from managers.styles import StyleManager
from utils.constants import LLM, Hotkey, Text, Theme, Timing

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.style_manager = StyleManager()
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.setWindowTitle(Text.SETTINGS_DIALOGUE_LABEL)
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel(Text.SETTINGS_DIALOGUE_LABEL)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Form layout for settings
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.config.get('api_key', ''))
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setObjectName("settingsInputField")
        self.api_key_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_API_KEY_PLACEHOLDER)
        self.api_key_input.setMinimumHeight(35)
        
        api_key_label = QLabel(Text.SETTINGS_DIALOGUE_API_KEY_LABEL)
        api_key_label.setObjectName("fieldLabel")
        form_layout.addRow(api_key_label, self.api_key_input)
        
        # API Base URL
        self.api_base_input = QLineEdit()
        self.api_base_input.setText(self.config.get('api_base', LLM.DEFAULT_API_BASE))
        self.api_base_input.setObjectName("settingsInputField")
        self.api_base_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_API_BASE_PLACEHOLDER)
        self.api_base_input.setMinimumHeight(35)
        
        api_base_label = QLabel(Text.SETTINGS_DIALOGUE_API_BASE_LABEL)
        api_base_label.setObjectName("fieldLabel")
        form_layout.addRow(api_base_label, self.api_base_input)
        
        # Model Name
        self.model_input = QLineEdit()
        self.model_input.setText(self.config.get('model', LLM.DEFAULT_LLM_MODEL))
        self.model_input.setObjectName("settingsInputField")
        self.model_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_LLM_MODEL_PLACEHOLDER)
        self.model_input.setMinimumHeight(35)
        
        model_label = QLabel("Model:")
        model_label.setObjectName("fieldLabel")
        form_layout.addRow(model_label, self.model_input)
        
        # Request Delay
        self.delay_input = QLineEdit()
        self.delay_input.setText(str(self.config.get('request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS)))
        self.delay_input.setObjectName("settingsInputField")
        self.delay_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_PLACEHOLDER)
        self.delay_input.setMinimumHeight(35)
        
        delay_label = QLabel(Text.SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_LABEL)
        delay_label.setObjectName("fieldLabel")
        form_layout.addRow(delay_label, self.delay_input)

        # Hotkey Configuration
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(self.config.get('hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW))
        self.hotkey_input.setObjectName("settingsInputField")
        self.hotkey_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_PLACEHOLDER)
        self.hotkey_input.setMinimumHeight(35)
        
        hotkey_label = QLabel(Text.SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_LABEL)
        hotkey_label.setObjectName("fieldLabel")
        form_layout.addRow(hotkey_label, self.hotkey_input)

        # Clear Previous Response Checkbox
        self.clear_previous_checkbox = QCheckBox("Clear previous response when window reopens")
        self.clear_previous_checkbox.setChecked(self.config.get('clear_previous_response', False))
        self.clear_previous_checkbox.setObjectName("settingsCheckBox")
        self.clear_previous_checkbox.setMinimumHeight(35)
        
        clear_label = QLabel("Auto Clear:")
        clear_label.setObjectName("fieldLabel")
        form_layout.addRow(clear_label, self.clear_previous_checkbox)

        # Theme Selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([Theme.CLASSIC, Theme.DARK])
        current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        theme_index = self.theme_combo.findText(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        self.theme_combo.setObjectName("settingsComboBox")
        self.theme_combo.setMinimumHeight(35)
        
        theme_label = QLabel("Theme:")
        theme_label.setObjectName("fieldLabel")
        form_layout.addRow(theme_label, self.theme_combo)
        
        layout.addLayout(form_layout)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveButton")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def apply_styles(self):
        """Apply styles using StyleManager."""
        self.setStyleSheet(self.style_manager.get_settings_dialog_styles())

    def save_settings(self):
        self.config.set('api_key', self.api_key_input.text())
        self.config.set('api_base', self.api_base_input.text())
        self.config.set('model', self.model_input.text())
        
        # Save request delay with validation
        try:
            delay = float(self.delay_input.text())
            if delay < 0.1:
                delay = 0.1
            elif delay > 10.0:
                delay = 10.0
            self.config.set('request_delay', delay)
        except ValueError:
            self.config.set('request_delay', 2.0)
            
        # Save hotkey
        hotkey_text = self.hotkey_input.text().strip()
        if hotkey_text:
            self.config.set('hotkey', hotkey_text)
        else:
            self.config.set('hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW)  # Default if empty

        self.config.set('clear_previous_response', self.clear_previous_checkbox.isChecked())
        self.config.set('theme', self.theme_combo.currentText())
            
        self.hide()