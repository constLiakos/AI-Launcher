import logging
from utils.constants import Theme
from PyQt5.QtGui import QFont, QFontDatabase

class StyleManager:
    """Manages all UI styles for the application."""
    def __init__(self, logger:logging.Logger):
        self.logger = logger.getChild('style_manager')

        self.current_theme = Theme.DEFAULT_THEME
        self.themes = {
            Theme.CLASSIC: self._get_light_theme()
        }
        
        self.button_styles = self.ButtonStyles(self)
    
    def set_theme(self, theme):
        """Set the current theme."""
        if theme in self.themes:
            old_theme = self.current_theme
            self.current_theme = theme
            self.logger.info(f"Theme changed from {old_theme} to {theme}")
        else:
            self.logger.warning(f"Attempted to set invalid theme: {theme}")

    def get_available_themes(self):
        themes = []
        for theme in self.themes.keys():
            themes.append(theme)
        return themes

    def get_theme_colors(self):
        """Get colors for current theme."""
        colors = self.themes[self.current_theme]
        # self.logger.debug(f"Retrieved colors for theme: {self.current_theme}")
        return colors
    
    def _get_light_theme(self):
        """Light theme with blue accents."""
        return {
            # === BRAND COLORS ===
            'brand_primary': "#5CA1F7",
            'brand_primary_hover': "#4A8AE8", 
            'brand_primary_active': "#3b82f6",
            'brand_secondary': '#8B5CF6',
            'brand_accent': '#EC4899',
            
            # === SEMANTIC COLORS ===
            'semantic_success': '#22C55E',
            'semantic_warning': '#856404',
            'semantic_warning_bg': '#fff3cd',
            'semantic_error': '#EF4444',
            'semantic_info': '#3B82F6',

            # === TEXT COLORS ===
            'text_primary': '#2d3142',
            'text_secondary': '#6b7280',
            'text_muted': '#9ca3af',
            'text_placeholder': '#9ca3af',
            'text_inverse': '#ffffff',
            'text_thinking': "#c6c7cf",
            'text_tertiary': '#9ca3af',
            'text_on_primary': '#ffffff',
            'text_on_secondary': '#374151',     


            # === BACKGROUND COLORS ===
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8fafc',
            'bg_tertiary': '#f3f4f6',
            'bg_elevated': 'rgba(248, 250, 252, 0.9)',
            'bg_overlay': 'rgba(255, 255, 255, 0.8)',
            'bg_window_start': '#f8fafc',
            'bg_window_end': '#e2e8f0',
            'bg_dialog_start': '#f8fafc',
            'bg_dialog_end': '#e2e8f0',
            'bg_conversation': 'rgba(248, 250, 252, 0.9)',

            # === MAIN  APP INPUT COLORS ===
            'main_input_bg': '#ffffff',
            'main_input_bg_focus': '#ffffff',
            'main_input_border': '#d1d5db',
            'main_input_border_focus': '#4f9cf9',

            # === SETTINGS INPUT COLORS ===
            'settings_input_bg': '#ffffff',
            'settings_input_bg_focus': '#ffffff',
            'settings_input_border': '#d1d5db',
            'settings_input_border_focus': '#4f9cf9',

            # === BUTTON COLORS ===
            'button_primary_bg': "#5CA1F7",
            'button_primary_hover': "#4A8AE8",
            'button_primary_active': "#3b82f6",
            'button_secondary_bg': '#f3f4f6',
            'button_secondary_hover': '#d1d5db',
            'button_secondary_active': '#9ca3af',
            'button_tertiary_bg': 'rgba(255, 255, 255, 0.4)',
            'button_tertiarty_border': 'rgba(79, 156, 249, 0.3)',
            'button_tertiarty_hover_bg': 'rgba(79, 156, 249, 0.1)',
            'button_tertiarty_hover_border': 'rgba(79, 156, 249, 0.5)',

            # === STATE COLORS ===
            'state_recording': "#e77c7c",
            'state_recording_hover': "#e25a5a",
            'state_active': "#5CA1F7",
            'state_inactive': '#9ca3af',

            # === COMPONENT SPECIFIC ===
            'history_accent': "#5CA1F7",
            'history_message_bg': "#ebf0f5",
            'conversation_border': 'rgba(79, 156, 249, 0.2)',
            'scrollbar_track': 'transparent',
            'scrollbar_thumb': 'rgba(79, 156, 249, 0.3)',
            'scrollbar_thumb_hover': 'rgba(79, 156, 249, 0.5)',

            # === SURFACE ALIASES (for easier migration) ===
            'surface_primary': '#ffffff',
            'surface_secondary': '#f8fafc',
            'surface_tertiary': '#f3f4f6',
            'surface_elevated': 'rgba(248, 250, 252, 0.9)',
            'surface_overlay': 'rgba(255, 255, 255, 0.8)',
            
            # === BORDER COLORS ===
            'border_subtle': 'rgba(79, 156, 249, 0.15)',     # Very light brand color
            'border_soft': 'rgba(209, 213, 219, 0.8)',       # Soft neutral
            'border_default': '#d1d5db',                      # Current input borders
            'border_focus': '#4f9cf9',                        # Focus states
            
            # === CONTAINER BORDERS ===
            'container_border': 'rgba(79, 156, 249, 0.12)',  # Main container
            'dialog_border': 'rgba(209, 213, 219, 0.6)',     # Dialogs
            'surface_border': 'rgba(148, 163, 184, 0.2)',    # General surfaces

        }

    def _get_settings_button_styles(self):
        """Get button styles for settings dialog."""
        colors = self.get_theme_colors()
        return f"""
        {self.button_styles.get_default_button()}


        #saveButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['brand_primary']}, stop:1 #3b82f6);  
            color: {colors['text_on_primary']};
            border: none;
        }}
        
        #saveButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6, stop:1 #2563eb);
        }}
        
        #saveButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563eb, stop:1 #1d4ed8);
        }}
        
        #cancelButton {{
        }}
        
        #cancelButton:hover {{
        }}

        """

    # === MAIN APPLICATION STYLES ===
    
    def _get_main_style(self):
        """Get the main application stylesheet."""
        colors = self.get_theme_colors()
        return f"""
        QMainWindow {{
            background: transparent;
        }}
        
        #mainContainer {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['bg_window_start']},
                stop:1 {colors['bg_window_end']});
            border-radius: 25px;
            border: 1px solid {colors['container_border']};
        }}
        """
    
    
    def _get_input_field_style(self):
        """Get input field styles for different states."""
        colors = self.get_theme_colors()
        return {
            'normal': f"""
            #inputField {{
                background: {colors['main_input_bg']};
                border: 2px solid {colors['main_input_border']};
                border-radius: 20px;
                padding: 15px 20px;
                font-size: 16px;
                color: {colors['text_primary']};
                font-weight: 400;
            }}
             
            #inputField:focus {{
                background: {colors['main_input_bg_focus']};
                border: 2px solid {colors['main_input_border_focus']};
                outline: none;
            }}
            
            #inputField::placeholder {{
                color: {colors['text_placeholder']};
                font-style: italic;
            }}
            """,
            'typing': f"""
            #inputFieldTyping {{
                background: {colors['main_input_bg']};
                border: 2px solid {colors['main_input_border']};
                border-radius: 20px;
                padding: 15px 20px;
                font-size: 16px;
                color: {colors['text_primary']};
                font-weight: 400;
            }}
            
            #inputFieldTyping:focus {{
                background: {colors['main_input_bg_focus']};
                border: 2px solid {colors['main_input_border_focus']};
                outline: none;
            }}
            
            #inputFieldTyping::placeholder {{
                color: {colors['text_placeholder']};
                font-style: italic;
            }}
            """
        }
    

    def get_animated_thinking_style(self, color):
        """Get animated thinking style with specific color."""
        colors = self.get_theme_colors()
        # self.logger.debug(f"Generated animated thinking style with color: {color}")
        return f"""
        #inputFieldThinking {{
            background: {colors['bg_primary']};
            border: 3px solid {color};
            border-radius: 20px;
            padding: 15px 20px;
            font-size: 16px;
            color: {colors['text_primary']};
            font-weight: 400;
        }}
        
        #inputFieldThinking:focus {{
            border: 3px solid {color};
            background: {colors['bg_primary']};
            outline: none;
        }}
        """
    
    def get_button_styles(self):
        """Get main application button styles."""
        colors = self.get_theme_colors()
        self.logger.debug("Generated main application button styles")
        return f"""

        #settingsButton, #multilineToggleButton, #multilineToggleButtonActive, #sttButton  {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['brand_primary']}, stop:1 #3b82f6);
            border: none;
            border-radius: 25px;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }}
        #settingsButton:hover, #multilineToggleButton:hover, #multilineToggleButtonActive:hover, #sttButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6, stop:1 #2563eb);
        }}
        #settingsButton:pressed, #multilineToggleButton:pressed, #multilineToggleButtonActive:pressed{{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563eb, stop:1 #1d4ed8);
        }}


        #sttButtonRecording {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['state_recording']}, stop:1 #ef5350);
            color: {colors['text_on_primary']};
            border: none;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
        }}
        #sttButtonRecording:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['state_recording']}, stop:1 #d32f2f);
            border: none;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
        }}

        #copyButton, #historyButton {{
            background: {colors['button_tertiary_bg']};
            border: 1px solid {colors['button_tertiarty_border']};
            border-radius: 8px;
            color: {colors['brand_primary']};
            font-size: 16px;
            padding: 2px;
        }}
        #copyButton:hover, #historyButton:hover {{
            background: {colors['button_tertiarty_hover_bg']};
            border: 1px solid {colors['button_tertiarty_hover_border']};
        }}

        #conversationToggleButton, #conversationToggleButtonExpanded {{
            background: {colors['button_tertiary_bg']};
            border: 1px solid {colors['button_tertiarty_border']};
            border-radius: 2px;
            color: {colors['brand_primary']};
        }}
        #conversationToggleButton:hover, #conversationToggleButtonExpanded:hover {{
            background: {colors['button_tertiarty_hover_bg']};
            border: 1px solid {colors['button_tertiarty_hover_border']};
        }}
        """
    
    def _get_thin_scrollbar_style(self):
        """Return modern thin scrollbar stylesheet."""
        colors = self.get_theme_colors()
        return f"""
        /* Modern thin scrollbar styles */
        /* Modern thin scrollbar styles */
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            border-radius: 4px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: rgba(79, 156, 249, 0.3);
            border-radius: 4px;
            min-height: 20px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: rgba(79, 156, 249, 0.5);
        }}

        QScrollBar::handle:vertical:pressed {{
            background: rgba(79, 156, 249, 0.7);
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
            background: transparent;
        }}

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: transparent;
        }}

        QScrollBar:horizontal {{
            height: 0px;
        }}
        """
    
    def get_complete_style(self, theme=None):
        """Get the complete stylesheet for main application."""
        if theme and theme != self.current_theme:
            old_theme = self.current_theme
            self.set_theme(theme)
            self.logger.debug(f"Temporarily switched to theme {theme} for style generation")
            style = (
                self._get_main_style() +
                self._get_input_field_style()['normal'] +
                self._get_input_field_style()['typing'] +
                self.get_button_styles() +
                self.get_conversation_area_style()
            )
            self.current_theme = old_theme
            self.logger.debug(f"Reverted to original theme: {old_theme}")
            return style
        
        self.logger.debug(f"Generated complete stylesheet for current theme: {self.current_theme}")
        return (
            self._get_main_style() +
            self._get_input_field_style()['normal'] +
            self._get_input_field_style()['typing'] +
            self.get_button_styles() +
            self.get_conversation_area_style()
        )
        
    def get_emoji_font(self):
        """Get emoji-compatible font for use in other components."""
        font = QFont()
        
        # For text content, prioritize readability fonts
        text_fonts = [
            "Ubuntu",              
            "Noto Sans",           
            "DejaVu Sans",         
            "Liberation Sans",     
            "Cantarell",          
            "Roboto",             
            "Segoe UI",           
            "Arial",              
        ]
        
        # For emoji support, we need color emoji fonts
        emoji_fonts = [
            "Noto Color Emoji",    # Primary Linux color emoji
            "Segoe UI Emoji",      # Windows
            "Apple Color Emoji",   # macOS
            "Twemoji",            # Web fallback
        ]
        
        font_db = QFontDatabase()
        
        # First, set a good text font
        for font_name in text_fonts:
            if font_name in font_db.families():
                font.setFamily(font_name)
                self.logger.debug(f"Selected text font: {font_name}")
                break
        
        # Build font families string to include emoji fallbacks
        available_fonts = []
        for font_name in text_fonts + emoji_fonts:
            if font_name in font_db.families():
                available_fonts.append(f"'{font_name}'")
        
        font_families = ", ".join(available_fonts)
        self.logger.debug(f"Font fallback chain: {font_families}")
        
        font.setPointSize(14)
        font.setStyleStrategy(QFont.PreferAntialias)
        
        # Store the font families string for CSS use
        self._font_families = font_families
        
        return font

    def get_widget_style(self):
        """Get style for combo boxes."""
        colors = self.get_theme_colors()
        return f"""
        QWidget{{
            background: {colors['bg_primary']};
            border: none;
            color: {colors['text_primary']};
        }}
        """
    
    def get_llm_thinking_style(self):
        colors = self.get_theme_colors()
        return f"font-style: italic; color: {colors['text_thinking']};"


#   ##########################################################################################
#       Conversation Area
#   ##########################################################################################

    def get_history_conversation_style(self):
        colors = self.get_theme_colors()
        return f"""
            #body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                background-color: {colors['bg_primary']};
                line-height: 1.4;
            }}
            .message-container {{ 
                margin: 12px 0; 
                width: 60%;
            }}
            .user-message-wrapper {{
                text-align: right;
                margin-left: 150px;
                border: 2px solid black;
                border-radius: 15px;
            }}
            .assistant-message-wrapper {{
                text-align: left;
                margin-right: 150px;
            }}
            .user-message {{ 
                color: {colors['text_primary']};
                border: 2px solid #007bff;
                border-radius: 18px 18px 4px 18px;
                word-wrap: break-word;
                text-align: right;
            }}
            .assistant-message {{ 
                color: {colors['text_primary']};
                border-radius: 18px 18px 18px 4px;
                border: 2px solid #333333;
                word-wrap: break-word;
                text-align: left;
            }}
            .system-message {{
                text-align: center;
                color: {colors['text_primary']};
                border: 1px solid #ffcc80;
                border-radius: 12px;
                margin: 15px auto;
                font-size: 14px;
                font-style: italic;
            }}
            .message-header-user {{
                font-size: 11px;
                color:{colors['history_accent']};
                margin-bottom: 6px;
                font-weight: bold;
                text-align: right;
            }}
            .message-header-assistant {{
                font-size: 11px;
                color: {colors['history_accent']};
                margin-bottom: 6px;
                font-weight: bold;
                text-align: left;
            }}
            .message-content {{
                font-size: 14px;
                line-height: 1.3;
                border-radius: 5px;
            }}
            .user-message .message-content {{
                color: {colors['text_primary']};
            }}
            .assistant-message .message-content {{
                color: {colors['text_primary']};
            }}
            .message-content p {{ 
                margin: 6px 0; 
            }}
            .message-content p:first-child {{ 
                margin-top: 0; 
            }}
            .message-content p:last-child {{ 
                margin-bottom: 0; 
            }}
            .message-content ul, .message-content ol {{ 
                margin: 6px 0; 
            }}
            .message-content code {{ 
                border-radius: 3px; 
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
            }}
            .user-message .message-content code {{
                color: {colors['text_primary']};
            }}
            .assistant-message .message-content code {{
                color: {colors['text_primary']};
            }}
    """

    def get_conversation_area_style(self):
        """Get response area styles."""
        colors = self.get_theme_colors()
        self.logger.debug("Generated response area styles")

        emoji_font = self.get_emoji_font()
        font_size = emoji_font.pointSize()
        
        # Use the font families chain for better emoji support
        font_families = getattr(self, '_font_families', "'Ubuntu', 'Noto Color Emoji'")
        
        return f"""
        #conversationArea {{
            background: {colors['bg_conversation']};
            border: 1px solid rgba(79, 156, 249, 0.2);
            border-radius: 15px;
            padding: 20px;
            font-size: {font_size}px;
            line-height: 1.6;
            color: {colors['text_primary']};
            font-family: {font_families};
        }}
        /* Modern thin scrollbar styles */
        { self._get_thin_scrollbar_style() }
        """

#   ##########################################################################################
#       Settings Dialog
#   ##########################################################################################

    # Settings - Main Dialog

    def get_settings_dialog_styles(self):
        """Get complete styles for settings dialog."""
        colors = self.get_theme_colors()
        self.logger.debug("Generated settings dialog styles")
        return f"""
        QDialog {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['bg_dialog_start']}, stop:1 {colors['bg_dialog_end']});
        }}
        
        #titleLabel {{
            font-size: 24px;
            font-weight: bold;
            color: {colors['text_primary']};
            margin-bottom: 10px;
        }}
        
        #scroll_area1 {{
            color: {colors['text_primary']};
            background: {colors['bg_primary']};
        }}
        
        #fieldLabel {{
            font-size: 14px;
            font-weight: 500;
            color: {colors['text_primary']};
            margin-bottom: 5px;
        }}
        
        #settingsInputField {{
            padding: 12px 16px;
            border: 2px solid {colors['settings_input_border']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['settings_input_bg']};
            color: {colors['text_primary']};
            min-height: 20px;
        }}
        
        #settingsInputField:focus {{
            border: 2px solid {colors['settings_input_border_focus']};
            outline: none;
            background: {colors['settings_input_bg_focus']};
        }}
        
        #settingsInputField::placeholder {{
            color: {colors['text_placeholder']};
        }}

        #settingsTextArea {{
            padding: 12px 16px;
            border: 2px solid {colors['settings_input_border']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['settings_input_bg']};
            color: {colors['text_primary']};
            min-height: 80px;
            font-family: monospace;
        }}

        #settingsTextArea:focus {{
            border: 2px solid {colors['settings_input_border_focus']};
            outline: none;
            background: {colors['settings_input_bg_focus']};
        }}
                
        QComboBox {{
            padding: 12px 16px;
            border: 2px solid {colors['settings_input_border']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['settings_input_bg']};
            color: {colors['text_primary']};
            min-height: 20px;
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors['settings_input_border_focus']};
            outline: none;
            background: {colors['settings_input_bg_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {colors['text_primary']};
            width: 6px;
            height: 6px;
            border-top: none;
            border-left: none;
            margin-right: 10px;
        }}
        
        QComboBox QAbstractItemView {{
            background: {colors['settings_input_bg']};
            color: {colors['text_primary']};
            border: 1px solid {colors['settings_input_border']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        {self._get_settings_button_styles()}
        """

    # Hotkey Recorder Dialog
    def get_hotkey_recorder_style(self):
        """Hotkey Recorder Widget Style"""
        colors = self.get_theme_colors()
        return f"""
        {self.button_styles.get_default_button()}
        #title{{
            color: {colors['text_primary']};
            border: none;
            padding: 12px 15px;
            font-size: 15px;
            font-weight: 500;
        }}
        #window{{
            color: {colors['text_primary']};
            background-color: {colors['bg_primary']}; 
            border: 2px solid {colors['border_default']};
            border-radius: 5px;
            padding: 15px 20px;
            font-size: 14px;
            font-weight: 400;
        }}
        #current_label{{
            color: {colors['text_primary']};
            font-size: 12px;
            font-weight: 300;
            font-style: italic;
        }}
        #hotkey_display{{
            color: {colors['text_primary']};
            border: none;
            font-size: 14px;
            font-weight: 400;
        }}
        #instructions{{
            color: {colors['text_primary']};
            background-color: {colors['bg_primary']}; 
            border: 2px solid {colors['border_default']};
            border-radius: 5px;
            padding: 5px 5px;
            font-size: 12px;
            font-weight: 400;
        }}  
        """
    
    # Settings - Dropdown Combobox
    def get_settings_combobox_style(self):
        """Get style for combo boxes."""
        colors = self.get_theme_colors()
        return f"""
        #settingsComboBox {{
            padding: 12px 16px;
            border: 2px solid {colors['settings_input_border']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['bg_primary']};
            color: {colors['text_primary']};
            min-height: 20px;
        }}
        #settingsComboBox:focus {{
            border: 2px solid {colors['border_focus']};
            outline: none;
            background: {colors['bg_primary']};
        }}
        
        /* Target dropdown with specific parent */
        #settingsComboBox QAbstractItemView {{
            border: 2px solid {colors['settings_input_border']} !important;
            border-radius: 8px !important;
            background: {colors['bg_primary']} !important;
            color: {colors['text_primary']} !important;
            selection-background-color: {colors['border_focus']} !important;
        }}
        #settingsComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            background: transparent;
        }}
        #settingsComboBox QAbstractItemView::item:hover {{
            background: {colors['bg_primary']} !important;
        }}
        #settingsComboBox QAbstractItemView::item:selected {{
            background: {colors['border_focus']} !important;
        }}
        """
    
    # Settings - Input Field 
    def get_settings_input_field_style(self):
        """Get style for input fields."""
        colors = self.get_theme_colors()
        return f"""
        QLineEdit {{
            padding: 12px 16px;
            border: 2px solid {colors['settings_input_border']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['bg_primary']};
            color: {colors['text_primary']};
            min-height: 20px;
        }}
        QLineEdit:focus {{
            border: 2px solid {colors['border_focus']};
            outline: none;
            background: {colors['bg_primary']};
        }}
        """

    def get_settings_textarea_style(self):
        """Get style for text areas."""
        colors = self.get_theme_colors()
        return f"""
        QTextEdit {{
            padding: 12px 16px;
            border: 2px solid {colors['settings_input_border']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['bg_primary']};
            color: {colors['text_primary']};
            font-family: monospace;
        }}
        QTextEdit:focus {{
            border: 2px solid {colors['border_focus']};
            outline: none;
            background: {colors['bg_primary']};
        }}
        """
    
# Button Styles
    class ButtonStyles:
        """Additional button style utilities."""
        
        def __init__(self, parent_instance):
            self.parent = parent_instance

        def get_default_button(self):
            colors = self.parent.get_theme_colors()
            return f"""
            QPushButton {{
                background: {colors['button_secondary_bg']};
                color: {colors['text_on_secondary']};
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 16px;
                min-width: 50px;
            }}
            QPushButton:hover {{
                background: {colors['button_secondary_hover']};
                color: {colors['text_on_secondary']};
            }}
            """
                
        def get_copy_button_success_style(self):
            """Get success style for copy button."""
            colors = self.parent.get_theme_colors()
            self.parent.logger.debug("Generated copy button success style")
            return f"""
            QPushButton {{
                background: {colors['semantic_success']};
                color: {colors['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            """
        def get_hotkeyRecorderBTN_style(self):
            colors = self.parent.get_theme_colors()
            self.parent.logger.debug("get_hotkeyRecorderBTN_style")
            return f"""
            #hotkeyRecorderBTN {{
                background: {colors['state_recording']};
                color: {colors['text_on_primary']};
                border: none
            }}
            
            #hotkeyRecorderBTN:hover {{
                background: {colors['state_recording_hover']};
            }}
            """