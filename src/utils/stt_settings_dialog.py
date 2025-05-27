import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QFrame, QCheckBox, QSizePolicy, QWidget)
from PyQt5.QtCore import Qt
from managers.style_manager import StyleManager
# Assuming you will add STT related constants here
from utils.constants import Text, STTDialogSize, STT # Placeholder for STT constants

class STTSettingsDialog(QDialog):
    def __init__(self, logger: logging.Logger, config, parent=None):
        super().__init__(parent)
        self.logger = logger.getChild('stt_settings_dialog')
        self.config = config
        self.style_manager = StyleManager(logger)
        
        self.setup_ui()
        self.load_settings()
        self.apply_styles()
        self._update_fields_enabled_state() # Initial state update

    def setup_ui(self):
        self.logger.debug("Setting up STTSettingsDialog UI")
        self._setup_window()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        layout.addWidget(self._create_title_label())
        
        self.form_widget = QWidget()
        self.form_widget.setObjectName("sttFormWidget")
        form_layout = self._create_form_layout(self.form_widget)
        layout.addWidget(self.form_widget)
        
        layout.addLayout(self._create_button_layout())
        
        self.setLayout(layout)
        self.logger.debug("STTSettingsDialog UI setup completed")

    def _setup_window(self):
        self.setWindowTitle("Speech-to-Text Settings")
        # Adjust size as needed, or make it dynamic
        self.setFixedSize(STTDialogSize.WINDOW_WIDTH - 50, STTDialogSize.WINDOW_HEIGHT - 150) 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

    def _create_title_label(self):
        title_label = QLabel("Speech-to-Text Settings")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        return title_label

    def _create_form_layout(self, parent_widget):
        form_layout = QFormLayout(parent_widget)
        form_layout.setSpacing(STTDialogSize.FORM_LAYOUT_SPACING)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Enable STT Checkbox
        self.enable_stt_checkbox = QCheckBox("Enable Speech-to-Text")
        self.enable_stt_checkbox.setObjectName("settingsCheckBox")
        self.enable_stt_checkbox.setMinimumHeight(35)
        self.enable_stt_checkbox.stateChanged.connect(self._update_fields_enabled_state)
        form_layout.addRow(self.enable_stt_checkbox)

        # STT API Key
        self.stt_api_key_input = self._create_input_field(
            '', "Enter STT API Key", is_password=True
        )
        form_layout.addRow(QLabel("STT API Key:"), self.stt_api_key_input)

        # STT API Base
        self.stt_api_base_input = self._create_input_field(
            STT.DEFAULT_API_BASE if hasattr(STT, 'DEFAULT_API_BASE') else '', "Enter STT API Base URL"
        )
        form_layout.addRow(QLabel("STT API Base:"), self.stt_api_base_input)

        # STT Model Name
        self.stt_model_input = self._create_input_field(
            STT.DEFAULT_MODEL if hasattr(STT, 'DEFAULT_MODEL') else '', "Enter STT Model Name"
        )
        form_layout.addRow(QLabel("STT Model:"), self.stt_model_input)
        
        # STT Hotkey
        self.stt_hotkey_input = self._create_input_field(
            STT.DEFAULT_HOTKEY if hasattr(STT, 'DEFAULT_HOTKEY') else '', "Enter STT Hotkey (e.g., Ctrl+Shift+S)"
        )
        form_layout.addRow(QLabel("STT Activation Hotkey:"), self.stt_hotkey_input)

        # STT Request Timeout
        self.stt_request_timeout_input = self._create_input_field(
            str(STT.DEFAULT_REQUEST_TIMEOUT) if hasattr(STT, 'DEFAULT_REQUEST_TIMEOUT') else '30', "Enter request timeout in seconds"
        )
        form_layout.addRow(QLabel("STT Request Timeout (s):"), self.stt_request_timeout_input)
        
        return form_layout

    def _create_input_field(self, default_value, placeholder, object_name="settingsInputField", is_password=False):
        field = QLineEdit()
        field.setText(str(default_value))
        field.setObjectName(object_name)
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(35)
        if is_password:
            field.setEchoMode(QLineEdit.Password)
        return field

    def _update_fields_enabled_state(self):
        enabled = self.enable_stt_checkbox.isChecked()
        self.stt_api_key_input.setEnabled(enabled)
        self.stt_api_base_input.setEnabled(enabled)
        self.stt_model_input.setEnabled(enabled)
        self.stt_hotkey_input.setEnabled(enabled)
        self.stt_request_timeout_input.setEnabled(enabled)
        self.logger.debug(f"STT fields enabled state: {enabled}")

    def _create_button_layout(self):
        button_layout = QHBoxLayout()
        button_layout.setSpacing(STTDialogSize.BUTTON_LAYOUT_SPACING)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setMinimumHeight(STTDialogSize.BUTTON_MIN_HEIGHT)
        cancel_btn.clicked.connect(self.hide)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveButton")
        save_btn.setMinimumHeight(STTDialogSize.BUTTON_MIN_HEIGHT)
        save_btn.clicked.connect(self.save_stt_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        return button_layout

    def load_settings(self):
        self.logger.debug("Loading STT settings")
        self.enable_stt_checkbox.setChecked(self.config.get('stt_enabled', False))
        
        self.stt_api_key_input.setText(self.config.get('stt_api_key', ''))
        api_key_value = self.config.get('stt_api_key', '')
        self.logger.debug(f"STT API key loaded: {'***' if api_key_value else 'empty'}")

        self.stt_api_base_input.setText(self.config.get('stt_api_base', STT.DEFAULT_API_BASE if hasattr(STT, 'DEFAULT_API_BASE') else ''))
        self.stt_model_input.setText(self.config.get('stt_model', STT.DEFAULT_MODEL if hasattr(STT, 'DEFAULT_MODEL') else ''))
        self.stt_hotkey_input.setText(self.config.get('stt_hotkey', STT.DEFAULT_HOTKEY if hasattr(STT, 'DEFAULT_HOTKEY') else ''))
        self.stt_request_timeout_input.setText(
            str(self.config.get('stt_request_timeout', STT.DEFAULT_REQUEST_TIMEOUT if hasattr(STT, 'DEFAULT_REQUEST_TIMEOUT') else 30))
        )
        self._update_fields_enabled_state()

    def save_stt_settings(self):
        self.logger.info("Saving STT settings")
        
        stt_enabled = self.enable_stt_checkbox.isChecked()
        self.config.set('stt_enabled', stt_enabled)
        self.logger.debug(f"STT enabled saved: {stt_enabled}")

        if stt_enabled:
            stt_api_key = self.stt_api_key_input.text()
            self.config.set('stt_api_key', stt_api_key)
            self.logger.debug(f"STT API key saved: {'***' if stt_api_key else 'empty'}")

            self.config.set('stt_api_base', self.stt_api_base_input.text())
            self.config.set('stt_model', self.stt_model_input.text())
            self.config.set('stt_hotkey', self.stt_hotkey_input.text().strip())
            try:
                timeout = int(self.stt_request_timeout_input.text())
                self.config.set('stt_request_timeout', timeout)
            except ValueError:
                self.logger.warning("Invalid STT request timeout value, using default.")
                default_timeout = STT.DEFAULT_REQUEST_TIMEOUT if hasattr(STT, 'DEFAULT_REQUEST_TIMEOUT') else 30
                self.config.set('stt_request_timeout', default_timeout)
                self.stt_request_timeout_input.setText(str(default_timeout)) # Update UI with default
        else:
            # Optionally clear or retain disabled fields
            self.config.set('stt_api_key', '') # Example: clear if disabled
            self.config.set('stt_api_base', STT.DEFAULT_API_BASE if hasattr(STT, 'DEFAULT_API_BASE') else '')
            self.config.set('stt_model', STT.DEFAULT_MODEL if hasattr(STT, 'DEFAULT_MODEL') else '')
            self.config.set('stt_hotkey', STT.DEFAULT_HOTKEY if hasattr(STT, 'DEFAULT_HOTKEY') else '')
            self.config.set('stt_request_timeout', STT.DEFAULT_REQUEST_TIMEOUT if hasattr(STT, 'DEFAULT_REQUEST_TIMEOUT') else 30)
            self.logger.debug("STT disabled, related fields reset to default/empty.")

        self.logger.info("STT settings saved successfully")
        self.hide()

    def apply_styles(self):
        self.logger.debug("Applying styles to STTSettingsDialog")
        current_theme = self.config.get('theme', 'Dark')
        self.style_manager.set_theme(current_theme)

        dialog_styles = self.style_manager.get_settings_dialog_styles()
        self.setStyleSheet(dialog_styles)
            
        input_style = self.style_manager.get_settings_input_field_style()
        for field in [self.stt_api_key_input, self.stt_api_base_input, 
                      self.stt_model_input, self.stt_hotkey_input]:
            field.setStyleSheet(input_style)
        
        # Apply style to the form widget background if needed
        form_widget_style = self.style_manager.get_widget_style()
        self.form_widget.setStyleSheet(form_widget_style)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_settings() # Reload settings each time it's shown
        self.logger.debug("STTSettingsDialog shown and settings reloaded.")
