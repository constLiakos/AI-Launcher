import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFormLayout, QCheckBox, QWidget, QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from pynput.keyboard import HotKey

from managers.style_manager import StyleManager
from utils.constants import STTDialogSize, STT, Text, Theme


class STTSettingsDialog(QDialog):
    settings_changed = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.style_manager = StyleManager()
        self._is_dragging = False
        self._drag_position = None

        self.setup_ui()
        self.load_settings()
        self.apply_styles()
        self._update_fields_enabled_state()  # Initial state update

    def setup_ui(self):
        self.logger.debug("Setting up STTSettingsDialog UI")
        self._setup_window()

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        layout.addWidget(self._create_title_label())

        # Add error message widget (initially hidden)
        self.error_message = self._create_error_message()
        layout.addWidget(self.error_message)

        self.form_widget = QWidget()
        self.form_widget.setObjectName("sttFormWidget")
        # form_layout = self._create_form_layout(self.form_widget)
        # layout.addWidget(self.form_widget)
        scroll_area = self._create_scroll_area()
        # Catchy this one, set transparent background
        scroll_area.setObjectName("scroll_area1")
        layout.addWidget(scroll_area)

        layout.addLayout(self._create_button_layout())

        self.setLayout(layout)
        self.logger.debug("STTSettingsDialog UI setup completed")

    def _setup_window(self):
        self.setWindowTitle("Speech-to-Text Settings")
        # Adjust size as needed, or make it dynamic
        self.setFixedSize(STTDialogSize.WINDOW_WIDTH - 50,
                          STTDialogSize.WINDOW_HEIGHT - 150)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

    def _update_fields_enabled_state(self):
        enabled = self.enable_stt_checkbox.isChecked()
        self.stt_api_key_input.setEnabled(enabled)
        self.stt_api_base_input.setEnabled(enabled)
        self.stt_model_input.setEnabled(enabled)
        self.stt_hotkey_input.setEnabled(enabled)
        self.stt_request_timeout_input.setEnabled(enabled)
        
        # Also enable/disable the hotkey recorder button
        hotkey_container = self.stt_hotkey_input.parent()
        if hotkey_container:
            for child in hotkey_container.children():
                if isinstance(child, QPushButton) and child.objectName() == "hotkeyRecorderBTN":
                    child.setEnabled(enabled)
                    break
        
        self.logger.debug(f"STT fields enabled state: {enabled}")

#   ##########################################################################################
#       Create UI Elements Functions
#   ##########################################################################################


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

    def _create_input_field(self, default_value, placeholder, object_name="settingsInputField", is_password=False):
        field = QLineEdit()
        field.setText(str(default_value))
        field.setObjectName(object_name)
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(35)
        if is_password:
            field.setEchoMode(QLineEdit.Password)
        return field

    def _create_title_label(self):
        title_label = QLabel("Speech-to-Text Settings")
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
        
        scroll_area.setWidget(self.form_widget)
        return scroll_area

    def _create_form_layout(self, parent_widget):
        form_layout = QFormLayout(parent_widget)
        form_layout.setSpacing(STTDialogSize.FORM_LAYOUT_SPACING)
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Define field configurations
        field_configs = [
            {
                'widget': self._create_enable_stt_checkbox(),
                'label': None,  # No label for checkbox as it has its own text
                'attr_name': 'enable_stt_checkbox'
            },
            {
                'widget': self._create_input_field('', "Enter STT API Key", is_password=True),
                'label': "STT API Key:",
                'attr_name': 'stt_api_key_input'
            },
            {
                'widget': self._create_input_field(
                    STT.DEFAULT_API_BASE if hasattr(STT, 'DEFAULT_API_BASE') else '', 
                    "Enter STT API Base URL"
                ),
                'label': "STT API Base:",
                'attr_name': 'stt_api_base_input'
            },
            {
                'widget': self._create_input_field(
                    STT.DEFAULT_MODEL if hasattr(STT, 'DEFAULT_MODEL') else '', 
                    "Enter STT Model Name"
                ),
                'label': "STT Model:",
                'attr_name': 'stt_model_input'
            },
            {
                'widget': self._create_stt_hotkey_field(),
                'label': "STT Activation Hotkey:",
                'attr_name': None
            },
            {
                'widget': self._create_input_field(
                    str(STT.DEFAULT_REQUEST_TIMEOUT) if hasattr(STT, 'DEFAULT_REQUEST_TIMEOUT') else '30', 
                    "Enter request timeout in seconds"
                ),
                'label': "STT Request Timeout (s):",
                'attr_name': 'stt_request_timeout_input'
            }
        ]

        # Add all fields to form
        for config in field_configs:
            widget = config['widget']
            if config['attr_name']:
                setattr(self, config['attr_name'], widget)
            
            if config['label'] is None:
                form_layout.addRow(widget)
            else:
                label = QLabel(config['label'])
                label.setObjectName("fieldLabel")
                form_layout.addRow(label, widget)

        return form_layout
    
    def _create_stt_hotkey_field(self):
        """Create STT hotkey input field with recorder button."""
        # Create container widget for hotkey input and button
        hotkey_container = QWidget()
        hotkey_layout = QHBoxLayout(hotkey_container)
        hotkey_layout.setContentsMargins(0, 0, 0, 0)
        hotkey_layout.setSpacing(8)
        
        # Create the input field
        stt_hotkey_input = self._create_input_field(
            STT.DEFAULT_HOTKEY if hasattr(STT, 'DEFAULT_HOTKEY') else '',
            "Enter STT Hotkey (e.g., Ctrl+Shift+S)"
        )
        
        # Create the recorder button
        hotkey_recorder_btn = QPushButton("Record")
        hotkey_recorder_btn.setObjectName("hotkeyRecorderBTN")
        hotkey_recorder_btn.setMinimumHeight(35)
        hotkey_recorder_btn.setMaximumWidth(80)
        hotkey_recorder_btn.clicked.connect(self._on_hotkey_recorder_clicked)
        
        # Add to layout
        hotkey_layout.addWidget(stt_hotkey_input)
        hotkey_layout.addWidget(hotkey_recorder_btn)
        
        # Store reference to input field for later access
        self.stt_hotkey_input = stt_hotkey_input
        self.hotkey_recorder_btn = hotkey_recorder_btn
        
        return hotkey_container
    
    def _create_enable_stt_checkbox(self):
        """Create the enable STT checkbox."""
        checkbox = QCheckBox("Enable Speech-to-Text")
        checkbox.setObjectName("settingsCheckBox")
        checkbox.setMinimumHeight(35)
        checkbox.stateChanged.connect(self._update_fields_enabled_state)
        return checkbox

#   ##########################################################################################
#       Hotkey Recorder Functions
#   ##########################################################################################

    def _on_hotkey_recorder_clicked(self):
        """Handle hotkey recorder button click."""
        from utils.hotkey_recorder import HotkeyRecorderDialog
        
        # Get current hotkey from config or input field
        current_hotkey = self.config.get('hotkey', '')  # or get from UI field
        
        dialog = HotkeyRecorderDialog(
            parent=self,
            current_hotkey=current_hotkey,
            title=Text.STT_HOTKEY_DIALOG_HOTKEY_TITLE,
            config=self.config
        )
        
        def on_hotkey_recorded(hotkey_string):
            self.logger.debug(f"Recorded hotkey: {hotkey_string}")
            self.stt_hotkey_input.setText(hotkey_string)
        
        dialog.hotkey_recorded.connect(on_hotkey_recorded)
        dialog.exec_()

#   ##########################################################################################
#       Load | Save Functions
#   ##########################################################################################

    def load_settings(self):
        self.logger.debug("Loading STT settings")
        self.enable_stt_checkbox.setChecked(
            self.config.get('stt_enabled', False))

        self.stt_api_key_input.setText(self.config.get('stt_api_key', ''))
        api_key_value = self.config.get('stt_api_key', '')
        self.logger.debug(
            f"STT API key loaded: {'***' if api_key_value else 'empty'}")

        self.stt_api_base_input.setText(self.config.get(
            'stt_api_base', STT.DEFAULT_API_BASE if hasattr(STT, 'DEFAULT_API_BASE') else ''))
        self.stt_model_input.setText(self.config.get(
            'stt_model', STT.DEFAULT_MODEL if hasattr(STT, 'DEFAULT_MODEL') else ''))
        self.stt_hotkey_input.setText(self.config.get(
            'stt_hotkey', STT.DEFAULT_HOTKEY if hasattr(STT, 'DEFAULT_HOTKEY') else ''))
        self.stt_request_timeout_input.setText(
            str(self.config.get('stt_request_timeout', STT.DEFAULT_REQUEST_TIMEOUT if hasattr(
                STT, 'DEFAULT_REQUEST_TIMEOUT') else 30))
        )
        self._update_fields_enabled_state()

    def save_stt_settings(self):
        self.logger.info("Saving STT settings")

        stt_enabled = self.enable_stt_checkbox.isChecked()
        self.config.set('stt_enabled', stt_enabled)
        self.logger.debug(f"STT enabled saved: {stt_enabled}")

        stt_api_key = self.stt_api_key_input.text()
        stt_api_base = self.stt_api_base_input.text()
        stt_model = self.stt_model_input.text()
        stt_hotkey = self.stt_hotkey_input.text().strip()


        if stt_enabled:
            # Check if any essential fields are not set
            if not stt_api_key or not stt_api_base or not stt_model or not self.stt_request_timeout_input.text():
                self.show_message(
                    "Please fill in all required STT fields.", 5000)
                self.logger.warning(
                    "Required STT fields not set, saving cancelled.")
                return  # Cancel the save operation

            self.config.set('stt_api_key', stt_api_key)
            self.logger.debug(
                f"STT API key saved: {'***' if stt_api_key else 'empty'}")

            if stt_enabled:
                self.config.set('stt_api_base', stt_api_base)
                self.config.set('stt_model', stt_model)

                if stt_hotkey:
                    try:
                        # Test if hotkey string is valid by attempting to create a HotKey object
                        test_hotkey = HotKey.parse(stt_hotkey)
                        self.config.set('stt_hotkey', stt_hotkey)
                        self.logger.debug(f"Hotkey saved: {stt_hotkey}")
                    except ValueError as e:
                        self.logger.error(f"Invalid hotkey format '{stt_hotkey}': {e}")
                        self._show_error_message(f"Invalid hotkey format. Please use format like 'ctrl+shift+f' or '<ctrl>+<shift>+f'")
                        return
                else:
                    self.logger.debug("Empty hotkey, using default")

                try:
                    timeout = int(self.stt_request_timeout_input.text())
                    self.config.set('stt_request_timeout', timeout)
                except ValueError:
                    self.logger.warning(
                        "Invalid STT request timeout value, using default.")
                    default_timeout = STT.DEFAULT_REQUEST_TIMEOUT if hasattr(
                        STT, 'DEFAULT_REQUEST_TIMEOUT') else 30
                    self.config.set('stt_request_timeout', default_timeout)
                    self.stt_request_timeout_input.setText(
                        str(default_timeout))  # Update UI with default
            else:
                # There is no need to reset fields, just save the enabled state
                self.logger.debug("STT disabled; no fields reset.")

        self.settings_changed.emit()

        self.logger.info("STT settings saved successfully")
        self.hide()

#   ##########################################################################################
#       Style Functions
#   ##########################################################################################

    def apply_styles(self):
        self.logger.debug("Applying styles to STTSettingsDialog")
        current_theme = self.config.get('theme', Theme.DEFAULT_THEME)
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
        self.hotkey_recorder_btn.setStyleSheet(self.style_manager.button_styles.get_hotkeyRecorderBTN_style())

    def showEvent(self, event):
        super().showEvent(event)
        self.load_settings()  # Reload settings each time it's shown
        self.logger.debug("STTSettingsDialog shown and settings reloaded.")

    def show_message(self, message, duration):
        # Create a temporary QLabel to show the message
        message_label = QLabel(message, self)
        message_label.setAlignment(Qt.AlignCenter)

        # Apply modern style to the message label
        message_label.setStyleSheet("""
            background-color: #f8d7da;  /* Light red background */
            color: #721c24;  /* Dark red text */
            border: 1px solid #f5c6cb;  /* Border color */
            border-radius: 5px;  /* Rounded corners */
            font-weight: bold;  /* Make the text bold */
            padding: 10px;  /* Padding around text */
            margin: 0 auto;  /* Center the label horizontally */
            width: calc(100% - 20px);   /* Width adjusted for padding */
        """)

        # Set geometry to position the message label below the title
        title_height = self.layout().itemAt(
            0).widget().height()  # Height of the title label
        # Position it below the title
        message_label.setGeometry(10, title_height + 10, self.width() - 20, 40)

        message_label.show()

        # Hide after the specified duration
        QTimer.singleShot(duration, message_label.hide)

#   ##########################################################################################
#       Popup Warning Messages Functions
#   ##########################################################################################

    def _create_error_message(self):
        """Create error message widget."""
        error_widget = QLabel()
        error_widget.setObjectName("errorMessage")
        error_widget.setAlignment(Qt.AlignCenter)
        error_widget.setWordWrap(True)
        error_widget.hide()  # Initially hidden
        error_widget.setMinimumHeight(0)
        error_widget.setMaximumHeight(60)
        error_widget.setContentsMargins(10, 5, 10, 5)
        
        # Apply warning style
        warning_style = """
            QLabel#errorMessage {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                color: #856404;
                font-weight: bold;
                padding: 8px 12px;
                margin: 5px 0px;
            }
        """
        error_widget.setStyleSheet(warning_style)
        
        return error_widget
    
    def _show_error_message(self, message):
        """Show error message in the dialog."""
        self.error_message.setText(message)
        self.error_message.show()
        QTimer.singleShot(5000, self.error_message.hide)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        self._drag_position = None
        event.accept()