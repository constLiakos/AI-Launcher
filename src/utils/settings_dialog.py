import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QFrame, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from managers.style_manager import StyleManager
from utils.about_dialog import AboutDialog
from utils.constants import LLM, Conversation, Hotkey, SettingsDialogSize, Text, Theme, Timing
from utils.version import VERSION

class SettingsDialog(QDialog):
    
    theme_changed = pyqtSignal(str)

    def __init__(self, logger:logging, config, parent=None):
        super().__init__(parent)
        self.logger = logger.getChild('settings_dialogue')
        self.config = config
        self.style_manager = StyleManager(logger)
        self.about_dialog = None
        self.setup_ui()
        self.apply_styles()
        self.original_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        self.logger.debug(f"SettingsDialog initialized with theme: {self.original_theme}")

    def setup_ui(self):
        self.logger.debug("Setting up SettingsDialog UI")
        self.setWindowTitle(Text.SETTINGS_DIALOGUE_LABEL)
        self.setFixedSize(SettingsDialogSize.WINDOW_WIDTH, SettingsDialogSize.WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(SettingsDialogSize.MAIN_LAYOUT_MARGIN, SettingsDialogSize.MAIN_LAYOUT_MARGIN, SettingsDialogSize.MAIN_LAYOUT_MARGIN, SettingsDialogSize.MAIN_LAYOUT_MARGIN)
        layout.setSpacing(SettingsDialogSize.MAIN_LAYOUT_SPACING)
        
        # Title
        title_label = QLabel(Text.SETTINGS_DIALOGUE_LABEL)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Form layout for settings
        form_layout = QFormLayout()
        form_layout.setSpacing(SettingsDialogSize.FORM_LAYOUT_SPACING)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # API Key
        self.api_key_input = QLineEdit()
        api_key_value = self.config.get('api_key', '')
        self.api_key_input.setText(api_key_value)
        self.logger.debug(f"API key loaded: {'***' if self.config.get('api_key', '') else 'empty'}")

        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setObjectName("settingsInputField")
        self.api_key_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_API_KEY_PLACEHOLDER)
        self.api_key_input.setMinimumHeight(35)
        api_key_label = QLabel(Text.SETTINGS_DIALOGUE_API_KEY_LABEL)
        api_key_label.setObjectName("fieldLabel")
        form_layout.addRow(api_key_label, self.api_key_input)
        
        # API Base URL
        self.api_base_input = QLineEdit()
        api_base_value = self.config.get('api_base', LLM.DEFAULT_API_BASE)
        self.api_base_input.setText(api_base_value)
        self.logger.debug(f"API base URL loaded: {api_base_value}")
        self.api_base_input.setObjectName("settingsInputField")
        self.api_base_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_API_BASE_PLACEHOLDER)
        self.api_base_input.setMinimumHeight(35)
        
        api_base_label = QLabel(Text.SETTINGS_DIALOGUE_API_BASE_LABEL)
        api_base_label.setObjectName("fieldLabel")
        form_layout.addRow(api_base_label, self.api_base_input)
        
        # Model Name
        self.model_input = QLineEdit()
        model_value = self.config.get('model', LLM.DEFAULT_LLM_MODEL)
        self.model_input.setText(model_value)
        self.logger.debug(f"Model loaded: {model_value}")
        self.model_input.setObjectName("settingsInputField")
        self.model_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_LLM_MODEL_PLACEHOLDER)
        self.model_input.setMinimumHeight(35)
        
        model_label = QLabel("Model:")
        model_label.setObjectName("fieldLabel")
        form_layout.addRow(model_label, self.model_input)

        # System Prompt
        self.system_prompt_input = QLineEdit()
        system_prompt_value = self.config.get('system_prompt', LLM.DEFAULT_SYSTEM_PROMPT)
        self.system_prompt_input.setText(system_prompt_value)
        self.logger.debug(f"System prompt loaded: {system_prompt_value[:50]}...")
        self.system_prompt_input.setObjectName("settingsInputField")
        self.system_prompt_input.setPlaceholderText("Enter system prompt for the LLM")
        self.system_prompt_input.setMinimumHeight(35)
        
        system_prompt_label = QLabel("System Prompt:")
        system_prompt_label.setObjectName("fieldLabel")
        form_layout.addRow(system_prompt_label, self.system_prompt_input)
        
        
        # Request Delay
        self.delay_input = QLineEdit()
        delay_value = self.config.get('request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS)
        self.delay_input.setText(str(delay_value))
        self.logger.debug(f"Request delay loaded: {delay_value}")
        self.delay_input.setObjectName("settingsInputField")
        self.delay_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_PLACEHOLDER)
        self.delay_input.setMinimumHeight(35)
        
        delay_label = QLabel(Text.SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_LABEL)
        delay_label.setObjectName("fieldLabel")
        form_layout.addRow(delay_label, self.delay_input)

        # Hotkey Configuration
        self.hotkey_input = QLineEdit()
        hotkey_value = self.config.get('hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW)
        self.hotkey_input.setText(hotkey_value)
        self.logger.debug(f"Hotkey loaded: {hotkey_value}")
        self.hotkey_input.setObjectName("settingsInputField")
        self.hotkey_input.setPlaceholderText(Text.SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_PLACEHOLDER)
        self.hotkey_input.setMinimumHeight(35)
        
        hotkey_label = QLabel(Text.SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_LABEL)
        hotkey_label.setObjectName("fieldLabel")
        form_layout.addRow(hotkey_label, self.hotkey_input)

        # Clear Previous Response Checkbox
        self.clear_previous_checkbox = QCheckBox(Text.SETTINGS_DIALOGUE_CLEAR_LAST_RESPONSE_ON_MINIMIZE_MESSAGE)
        clear_previous_value = self.config.get('clear_last_response_on_minimize', Conversation.DEFAULT_CLEAR_LAST_RESPONSE_ON_MINIMIZE)
        self.clear_previous_checkbox.setChecked(clear_previous_value)
        self.logger.debug(f"Clear previous response loaded: {clear_previous_value}")
        self.clear_previous_checkbox.setObjectName("settingsCheckBox")
        self.clear_previous_checkbox.setMinimumHeight(35)
        
        clear_label = QLabel(Text.SETTINGS_DIALOGUE_CLEAR_LAST_RESPONSE_ON_MINIMIZE_LABEL)
        clear_label.setObjectName("fieldLabel")
        form_layout.addRow(clear_label, self.clear_previous_checkbox)

        # Clear History on Hide Checkbox
        self.clear_history_on_minimize_checkbox = QCheckBox(Text.SETTINGS_DIALOGUE_CLEAR_CONVERSATION_HISTORY_ON_MINIMIZE_MESSAGE)
        clear_history_on_minimize_value = self.config.get('clear_history_on_minimize', Conversation.DEFAULT_CLEAR_HISTORY_ON_MINIMIZE)
        self.clear_history_on_minimize_checkbox.setChecked(clear_history_on_minimize_value)
        self.logger.debug(f"Clear history on hide loaded: {clear_history_on_minimize_value}")
        self.clear_history_on_minimize_checkbox.setObjectName("settingsCheckBox")
        self.clear_history_on_minimize_checkbox.setMinimumHeight(35)
        
        clear_history_label = QLabel(Text.SETTINGS_DIALOGUE_CLEAR_CONVERSATION_HISTORY_ON_MINIMIZE_LABEL)
        clear_history_label.setObjectName("fieldLabel")
        form_layout.addRow(clear_history_label, self.clear_history_on_minimize_checkbox)

        # Message History Limit
        self.message_history_input = QLineEdit()
        history_limit_value = self.config.get('message_history_limit', Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT)
        self.message_history_input.setText(str(history_limit_value))
        self.logger.debug(f"Message history limit loaded: {history_limit_value}")
        self.message_history_input.setObjectName("settingsInputField")
        self.message_history_input.setPlaceholderText("Enter number of messages to keep (1-100)")
        self.message_history_input.setMinimumHeight(35)
        
        history_label = QLabel("Message History Limit:")
        history_label.setObjectName("fieldLabel")
        form_layout.addRow(history_label, self.message_history_input)

        # Theme Selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([Theme.CLASSIC, Theme.DARK])
        current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        theme_index = self.theme_combo.findText(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        self.logger.debug(f"Theme loaded: {current_theme}")
        self.theme_combo.setObjectName("settingsComboBox")
        self.theme_combo.setMinimumHeight(35)
        
        theme_label = QLabel("Theme:")
        theme_label.setObjectName("fieldLabel")
        form_layout.addRow(theme_label, self.theme_combo)
        
        layout.addLayout(form_layout)        
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SettingsDialogSize.BUTTON_LAYOUT_SPACING)
        
        # About button (left side)
        about_btn = QPushButton("About")
        about_btn.setObjectName("aboutButton")
        about_btn.setMinimumHeight(SettingsDialogSize.BUTTON_MIN_HEIGHT)
        about_btn.clicked.connect(self.show_about_dialog)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setMinimumHeight(SettingsDialogSize.BUTTON_MIN_HEIGHT)
        cancel_btn.clicked.connect(self.hide)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveButton")
        save_btn.setMinimumHeight(SettingsDialogSize.BUTTON_MIN_HEIGHT)
        save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(about_btn)
        button_layout.addStretch()  # Add space between About and Cancel/Save
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.logger.debug("SettingsDialog UI setup completed")
        
    def apply_styles(self):
        """Apply styles using StyleManager."""
        self.logger.debug("Applying styles to SettingsDialog")
        self.setStyleSheet(self.style_manager.get_settings_dialog_styles())

    def save_settings(self):
        self.logger.info("Saving settings")

        # API Key
        api_key = self.api_key_input.text()
        self.config.set('api_key', api_key)
        self.logger.debug(f"API key saved: {'***' if api_key else 'empty'}")
        
        # API Base
        api_base = self.api_base_input.text()
        self.config.set('api_base', api_base)
        self.logger.debug(f"API base saved: {api_base}")
        
        # Model
        model = self.model_input.text()
        self.config.set('model', model)
        self.logger.debug(f"Model saved: {model}")

        # System Prompt
        system_prompt = self.system_prompt_input.text()
        self.config.set('system_prompt', system_prompt)
        self.logger.debug(f"System prompt saved: {system_prompt[:50]}...")
        
        # Save request delay with validation
        try:
            delay = float(self.delay_input.text())
            if delay < 0.1:
                delay = 0.1
                self.logger.warning(f"Request delay too low, setting to minimum: {delay}")
            elif delay > 10.0:
                delay = 10.0
                self.logger.warning(f"Request delay too high, setting to maximum: {delay}")
            self.config.set('request_delay', delay)
            self.logger.debug(f"Request delay saved: {delay}")
        except ValueError as e:
            self.logger.error(f"Invalid delay value '{self.delay_input.text()}': {e}, using default")
            self.config.set('request_delay', 2.0)
            
        # Save hotkey
        hotkey_text = self.hotkey_input.text().strip()
        if hotkey_text:
            self.config.set('hotkey', hotkey_text)
            self.logger.debug(f"Hotkey saved: {hotkey_text}")
        else:
            self.config.set('hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW)
            self.logger.debug("Empty hotkey, using default")

       # Clear previous response
        clear_previous = self.clear_previous_checkbox.isChecked()
        self.config.set('clear_last_response_on_minimize', clear_previous)
        self.logger.debug(f"Clear previous response saved: {clear_previous}")

        # Clear history on hide
        clear_history_on_minimize = self.clear_history_on_minimize_checkbox.isChecked()
        self.config.set('clear_history_on_minimize', clear_history_on_minimize)
        self.logger.debug(f"Clear history on hide saved: {clear_history_on_minimize}")


        # Save message history limit with validation
        try:
            history_limit = int(self.message_history_input.text())
            if history_limit < 1:
                history_limit = 1
                self.logger.warning(f"Message history limit too low, setting to minimum: {history_limit}")
            elif history_limit > 100:
                history_limit = 100
                self.logger.warning(f"Message history limit too high, setting to maximum: {history_limit}")
            self.config.set('message_history_limit', history_limit)
            self.logger.debug(f"Message history limit saved: {history_limit}")
        except ValueError as e:
            self.logger.error(f"Invalid message history limit value '{self.message_history_input.text()}': {e}, using default")
            self.config.set('message_history_limit', Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT)
        
        # Save theme
        new_theme = self.theme_combo.currentText()
        self.config.set('theme', new_theme)
        self.logger.debug(f"Theme saved: {new_theme}")
        
        # Emit signal if theme changed
        if new_theme != self.original_theme:
            self.logger.info(f"Theme changed from {self.original_theme} to {new_theme}")
            self.theme_changed.emit(new_theme)
        
        self.logger.info("Settings saved successfully")
        self.hide()

    def show_about_dialog(self):
        """Show the About dialog."""
        self.logger.debug("Opening About dialog")
        if self.about_dialog is None:
            self.about_dialog = AboutDialog(self.logger, self)
        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.activateWindow()