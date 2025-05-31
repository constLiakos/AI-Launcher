import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFormLayout, QFrame, QCheckBox, QComboBox, QTextEdit, QSizePolicy, QWidget, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from managers.style_manager import StyleManager
from utils.about_dialog import AboutDialog
from utils.constants import LLM, Conversation, Hotkey, SettingsDialogSize, Text, Theme, Timing
from utils.stt_settings_dialog import STTSettingsDialog
from utils.version import VERSION

class SettingsDialog(QDialog):
    theme_changed = pyqtSignal(str)
    
    def __init__(self, logger: logging.Logger, config, parent=None):
        super().__init__(parent)
        self.logger = logger.getChild('settings_dialogue')
        self.config = config
        self.style_manager = StyleManager(logger)
        self.about_dialog = None
        self.stt_settings_dialog = None
        
        # Store original theme for comparison
        self.original_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        self.logger.debug(f"SettingsDialog initialized with theme: {self.original_theme}")
        
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.logger.debug("Setting up SettingsDialog UI")
        self._setup_window()
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(
            SettingsDialogSize.MAIN_LAYOUT_MARGIN, SettingsDialogSize.MAIN_LAYOUT_MARGIN,
            SettingsDialogSize.MAIN_LAYOUT_MARGIN, SettingsDialogSize.MAIN_LAYOUT_MARGIN
        )
        layout.setSpacing(SettingsDialogSize.MAIN_LAYOUT_SPACING)
        
        # Add components
        layout.addWidget(self._create_title_label())
        
        scroll_area = self._create_scroll_area()
        # Catchy this one, set transparent background
        scroll_area.setObjectName("scroll_area1")
        layout.addWidget(scroll_area)
        
        layout.addLayout(self._create_button_layout())
        layout.setStretchFactor(scroll_area, 1)
        
        self.setLayout(layout)
        self.logger.debug("SettingsDialog UI setup completed")

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle(Text.SETTINGS_DIALOGUE_LABEL)
        self.setFixedSize(SettingsDialogSize.WINDOW_WIDTH, SettingsDialogSize.WINDOW_HEIGHT)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

    def _create_title_label(self):
        """Create and configure title label."""
        title_label = QLabel(Text.SETTINGS_DIALOGUE_LABEL)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        return title_label

    def _create_scroll_area(self):
        """Create scroll area with form layout."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.form_widget = QWidget()
        self.form_widget.setObjectName("formWidget")
        form_layout = self._create_form_layout(self.form_widget)
        
        scroll_area.setWidget(self.form_widget) # MODIFIED: Use self.form_widget
        return scroll_area

    def _create_form_layout(self, parent_widget):
        """Create and populate form layout with all settings fields."""
        form_layout:QFormLayout = QFormLayout(parent_widget)
        form_layout.setSpacing(SettingsDialogSize.FORM_LAYOUT_SPACING)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        
        # Define field configurations
        field_configs = [
            {
                'widget': self._create_api_key_field(),
                'label': Text.SETTINGS_DIALOGUE_API_KEY_LABEL,
                'attr_name': 'api_key_input'
            },
            {
                'widget': self._create_api_base_field(),
                'label': Text.SETTINGS_DIALOGUE_API_BASE_LABEL,
                'attr_name': 'api_base_input'
            },
            {
                'widget': self._create_model_field(),
                'label': "Model:",
                'attr_name': 'model_input'
            },
            {
                'widget': self._create_system_prompt_field(),
                'label': "System Prompt:",
                'attr_name': 'system_prompt_input'
            },
            {
                'widget': self._create_delay_field(),
                'label': Text.SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_LABEL,
                'attr_name': 'delay_input'
            },
            {
                'widget': self._create_hotkey_field(),
                'label': Text.SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_LABEL,
                'attr_name': 'hotkey_input'
            },
            {
                'widget': self._create_clear_previous_checkbox(),
                'label': Text.SETTINGS_DIALOGUE_CLEAR_LAST_RESPONSE_ON_MINIMIZE_LABEL,
                'attr_name': 'clear_previous_checkbox'
            },
            {
                'widget': self._create_clear_history_checkbox(),
                'label': Text.SETTINGS_DIALOGUE_CLEAR_CONVERSATION_HISTORY_ON_MINIMIZE_LABEL,
                'attr_name': 'clear_history_on_minimize_checkbox'
            },
            {
                'widget': self._create_message_history_field(),
                'label': "Message History Limit:",
                'attr_name': 'message_history_input'
            },
            {
                'widget': self._create_theme_combo(),
                'label': "Theme:",
                'attr_name': 'theme_combo'
            }
        ]
        
        # Add all fields to form
        for config in field_configs:
            label = QLabel(config['label'])
            label.setObjectName("fieldLabel")
            widget_it:QWidget = config['widget']
            widget_it.setContentsMargins(0, 0, 40, 0)
            setattr(self, config['attr_name'], widget_it)
            form_layout.addRow(label, widget_it)
        
        return form_layout

    def _create_input_field(self, config_key, default_value, placeholder, object_name="settingsInputField"):
        """Create a standard input field with common properties."""
        field = QLineEdit()
        value = self.config.get(config_key, default_value)
        field.setText(str(value))
        field.setObjectName(object_name)
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(35)
        self.logger.debug(f"{config_key} loaded: {value}")
        return field

    def _create_api_key_field(self):
        """Create API key input field."""
        field = self._create_input_field(
            'api_key', '', Text.SETTINGS_DIALOGUE_API_KEY_PLACEHOLDER
        )
        field.setEchoMode(QLineEdit.Password)
        # Log masked value for security
        api_key_value = self.config.get('api_key', '')
        self.logger.debug(f"API key loaded: {'***' if api_key_value else 'empty'}")
        return field

    def _create_api_base_field(self):
        """Create API base URL input field."""
        return self._create_input_field(
            'api_base', LLM.DEFAULT_API_BASE, Text.SETTINGS_DIALOGUE_API_BASE_PLACEHOLDER
        )

    def _create_model_field(self):
        """Create model name input field."""
        return self._create_input_field(
            'model', LLM.DEFAULT_LLM_MODEL, Text.SETTINGS_DIALOGUE_LLM_MODEL_PLACEHOLDER
        )

    def _create_system_prompt_field(self):
        """Create system prompt text area."""
        field = QTextEdit()
        value = self.config.get('system_prompt', LLM.DEFAULT_SYSTEM_PROMPT)
        field.setPlainText(value)
        field.setObjectName("settingsTextArea")
        field.setPlaceholderText("Enter system prompt for the LLM")
        field.setMinimumHeight(SettingsDialogSize.SYSTEM_PROMPT_MIN)
        field.setMaximumHeight(SettingsDialogSize.SYSTEM_PROMPT_MAX)
        field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.logger.debug(f"System prompt loaded: {value[:50]}...")
        return field

    def _create_delay_field(self):
        """Create request delay input field."""
        return self._create_input_field(
            'request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS,
            Text.SETTINGS_DIALOGUE_REQUEST_DELAY_PLACEHOLDER_PLACEHOLDER
        )

    def _create_hotkey_field(self):
        """Create hotkey input field."""
        return self._create_input_field(
            'hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW,
            Text.SETTINGS_DIALOGUE_HOTKEY_TOGGLE_MINIMIZE_WINDOW_PLACEHOLDER
        )

    def _create_checkbox_field(self, config_key, default_value, text, object_name="settingsCheckBox"):
        """Create a standard checkbox field."""
        checkbox = QCheckBox(text)
        value = self.config.get(config_key, default_value)
        checkbox.setChecked(value)
        checkbox.setObjectName(object_name)
        checkbox.setMinimumHeight(35)
        self.logger.debug(f"{config_key} loaded: {value}")
        return checkbox

    def _create_clear_previous_checkbox(self):
        """Create clear previous response checkbox."""
        return self._create_checkbox_field(
            'clear_last_response_on_minimize',
            Conversation.DEFAULT_CLEAR_LAST_RESPONSE_ON_MINIMIZE,
            Text.SETTINGS_DIALOGUE_CLEAR_LAST_RESPONSE_ON_MINIMIZE_MESSAGE
        )

    def _create_clear_history_checkbox(self):
        """Create clear history on minimize checkbox."""
        return self._create_checkbox_field(
            'clear_history_on_minimize',
            Conversation.DEFAULT_CLEAR_HISTORY_ON_MINIMIZE,
            Text.SETTINGS_DIALOGUE_CLEAR_CONVERSATION_HISTORY_ON_MINIMIZE_MESSAGE
        )

    def _create_message_history_field(self):
        """Create message history limit input field."""
        return self._create_input_field(
            'message_history_limit', Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT,
            "Enter number of messages to keep (1-100)"
        )

    def _create_theme_combo(self):
        """Create theme selection combo box."""
        combo = QComboBox()
        combo.addItems([Theme.CLASSIC, Theme.DARK])
        current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        theme_index = combo.findText(current_theme)
        if theme_index >= 0:
            combo.setCurrentIndex(theme_index)
        combo.setObjectName("settingsComboBox")
        combo.setMinimumHeight(35)
        self.logger.debug(f"Theme loaded: {current_theme}")
        return combo

    def _create_button_layout(self):
        """Create button layout with About, Cancel, and Save buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SettingsDialogSize.BUTTON_LAYOUT_SPACING)
        
        # About button (left side)
        about_btn = QPushButton("About")
        about_btn.setObjectName("aboutButton")
        about_btn.setMinimumHeight(SettingsDialogSize.BUTTON_MIN_HEIGHT)
        about_btn.clicked.connect(self.show_about_dialog)

        # STT Settings button (middle-left)
        stt_settings_btn = QPushButton("STT Settings")
        stt_settings_btn.setObjectName("sttSettingsButton")
        stt_settings_btn.setMinimumHeight(SettingsDialogSize.BUTTON_MIN_HEIGHT)
        stt_settings_btn.clicked.connect(self.show_stt_settings_dialog)
        
        # Cancel and Save buttons (right side)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setMinimumHeight(SettingsDialogSize.BUTTON_MIN_HEIGHT)
        cancel_btn.clicked.connect(self.hide)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("saveButton")
        save_btn.setMinimumHeight(SettingsDialogSize.BUTTON_MIN_HEIGHT)
        save_btn.clicked.connect(self.save_settings)
        
        button_layout.addWidget(about_btn)
        button_layout.addWidget(stt_settings_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        return button_layout

    def apply_styles(self):
        """Apply styles using StyleManager."""
        self.logger.debug("Applying styles to SettingsDialog")

        # Set the current theme in style manager
        current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
        self.style_manager.set_theme(current_theme)

        # Apply settings dialog styles
        settings_styles = self.style_manager.get_settings_dialog_styles()
        self.setStyleSheet(settings_styles)
            
        
        # Apply input field styles
        input_style = self.style_manager.get_settings_input_field_style()
        input_fields = [
            self.api_key_input, self.api_base_input, self.model_input,
            self.delay_input, self.hotkey_input, self.message_history_input
        ]
        
        for field in input_fields:
            field.setStyleSheet(input_style)
        
        # Apply specialized styles
        self.system_prompt_input.setStyleSheet(self.style_manager.get_settings_textarea_style())
        self.theme_combo.setStyleSheet(self.style_manager.get_settings_combobox_style())

        stt_settings_button = self.findChild(QPushButton, "sttSettingsButton")
        if stt_settings_button:
            button_style = self.style_manager.button_styles.get_stt_settings_button()
            if button_style:
                 stt_settings_button.setStyleSheet(button_style)

        form_widget_style = self.style_manager.get_widget_style()
        self.form_widget.setStyleSheet(form_widget_style)

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
        system_prompt = self.system_prompt_input.toPlainText().strip()
        if not system_prompt:
            system_prompt = LLM.DEFAULT_SYSTEM_PROMPT
            self.logger.debug("Empty system prompt, using default.")
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
        self.accept()

    def show_about_dialog(self):
        """Show the About dialog."""
        self.logger.debug("Opening About dialog")
        if self.about_dialog is None:
            self.about_dialog = AboutDialog(self.logger, self)
        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.activateWindow()

    def show_stt_settings_dialog(self):
        """Show the STT Settings dialog."""
        self.logger.debug("Opening STT Settings dialog")
        if self.stt_settings_dialog is None:
            self.stt_settings_dialog = STTSettingsDialog(self.logger.parent, self.config, self)
            current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
            self.stt_settings_dialog.style_manager.set_theme(current_theme)
            self.stt_settings_dialog.apply_styles() 
            self.stt_settings_dialog.load_settings()

            # Connect the settings_changed signal to the desired slot in Launcher
            self.stt_settings_dialog.settings_changed.connect(self.parent().on_stt_settings_changed)

            self.stt_settings_dialog.show()
            self.stt_settings_dialog.raise_()
            self.stt_settings_dialog.activateWindow()