from utils.constants import BackgroundColors, Theme


class StyleManager:
    """Manages all UI styles for the application."""
    def __init__(self):
        self.current_theme = Theme.DEFAULT_THEME
        self.themes = {
            Theme.CLASSIC: self._get_classic_theme(),
            Theme.DARK: self._get_dark_theme()
        }
        
        self.button_styles = self.ButtonStyles(self)
    
    def set_theme(self, theme):
        """Set the current theme."""
        if theme in self.themes:
            self.current_theme = theme

    def get_theme_colors(self):
        """Get colors for current theme."""
        return self.themes[self.current_theme]
    
    def _get_classic_theme(self):
        """Classic theme colors."""
        return {
            'primary': '#4F9CF9',
            'secondary': '#8B5CF6',
            'success': '#22C55E',
            'error': '#EF4444',
            'warning': '#F97316',
            'pink': '#EC4899',
            'white': '#FFFFFF',
            'dark': '#2D3142',
            'transparent_white': 'rgba(255, 255, 255, 0.8)',
            'window_bg_start': '#f8fafc',
            'window_bg_end': '#e2e8f0',
            'field_bg': '#ffffff',
            'field_bg_focus': '#ffffff',
            'border_normal': '#d1d5db',
            'border_focus': '#4f9cf9',
            'placeholder': '#9ca3af',
            'text_color': '#2d3142',
            'dialog_bg_start': '#f8fafc',
            'dialog_bg_end': '#e2e8f0',
            'response_bg': 'rgba(248, 250, 252, 0.9)',
            'button_secondary_bg': '#f3f4f6',
            'button_secondary_text': '#374151'
        }
    
    def _get_dark_theme(self):
        """Dark theme colors."""
        return {
            'primary': '#4F9CF9',
            'secondary': '#8B5CF6',
            'success': '#22C55E',
            'error': '#EF4444',
            'warning': '#F97316',
            'pink': '#EC4899',
            'white': '#FFFFFF',
            'dark': '#2D3142',
            'transparent_white': 'rgba(255, 255, 255, 0.1)',
            'window_bg_start': '#2d3142',
            'window_bg_end': '#1a1d29',
            'field_bg': '#374151',
            'field_bg_focus': '#4b5563',
            'border_normal': '#4a5568',
            'border_focus': '#4f9cf9',
            'placeholder': '#9ca3af',
            'text_color': '#ffffff',
            'dialog_bg_start': '#2d3142',
            'dialog_bg_end': '#1a1d29',
            'response_bg': 'rgba(55, 65, 81, 0.9)',
            'button_secondary_bg': '#4b5563',
            'button_secondary_text': '#ffffff'
        }

    # === SETTINGS DIALOG STYLES ===
    def get_settings_dialog_styles(self):
        """Get complete styles for settings dialog."""
        colors = self.get_theme_colors()
        return f"""
        QDialog {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors['dialog_bg_start']}, stop:1 {colors['dialog_bg_end']});
        }}
        
        #titleLabel {{
            font-size: 24px;
            font-weight: bold;
            color: {colors['text_color']};
            margin-bottom: 10px;
        }}
        
        #fieldLabel {{
            font-size: 14px;
            font-weight: 500;
            color: {colors['text_color']};
            margin-bottom: 5px;
        }}
        
        #settingsInputField {{
            padding: 12px 16px;
            border: 2px solid {colors['border_normal']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['field_bg']};
            color: {colors['text_color']};
            min-height: 20px;
        }}
        
        #settingsInputField:focus {{
            border: 2px solid {colors['border_focus']};
            outline: none;
            background: {colors['field_bg_focus']};
        }}
        
        #settingsInputField::placeholder {{
            color: {colors['placeholder']};
        }}
        
        QComboBox {{
            padding: 12px 16px;
            border: 2px solid {colors['border_normal']};
            border-radius: 12px;
            font-size: 14px;
            background: {colors['field_bg']};
            color: {colors['text_color']};
            min-height: 20px;
        }}
        
        QComboBox:focus {{
            border: 2px solid {colors['border_focus']};
            outline: none;
            background: {colors['field_bg_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {colors['text_color']};
            width: 6px;
            height: 6px;
            border-top: none;
            border-left: none;
            margin-right: 10px;
        }}
        
        QComboBox QAbstractItemView {{
            background: {colors['field_bg']};
            color: {colors['text_color']};
            border: 1px solid {colors['border_normal']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        {self._get_settings_button_styles()}
        """


    def _get_settings_button_styles(self):
        """Get button styles for settings dialog."""
        colors = self.get_theme_colors()
        return f"""
        #saveButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['primary']}, stop:1 #3b82f6);
            color: {colors['white']};
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            min-width: 100px;
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
            background: {colors['button_secondary_bg']};
            color: {colors['button_secondary_text']};
            border: 2px solid {colors['border_normal']};
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            min-width: 100px;
        }}
        
        #cancelButton:hover {{
            background: {colors['border_normal']};
            color: {colors['button_secondary_text']};
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
                stop:0 {colors['window_bg_start']},
                stop:1 {colors['window_bg_end']});
            border-radius: 25px;
            border: 1px solid {colors['border_normal']};
        }}
        """
    
    
    def _get_input_field_style(self):
        """Get input field styles for different states."""
        colors = self.get_theme_colors()
        return {
            'normal': f"""
            #inputField {{
                background: {colors['field_bg']};
                border: 2px solid {colors['border_normal']};
                border-radius: 20px;
                padding: 15px 20px;
                font-size: 16px;
                color: {colors['text_color']};
                font-weight: 400;
            }}
            
            #inputField:focus {{
                border: 2px solid {colors['border_focus']};
                background: {colors['field_bg_focus']};
                outline: none;
            }}
            
            #inputField::placeholder {{
                color: {colors['placeholder']};
                font-style: italic;
            }}
            """,
            'typing': f"""
            #inputFieldTyping {{
                background: {colors['field_bg']};
                border: 2px solid {colors['primary']};
                border-radius: 20px;
                padding: 15px 20px;
                font-size: 16px;
                color: {colors['text_color']};
                font-weight: 400;
            }}
            
            #inputFieldTyping:focus {{
                border: 2px solid {colors['border_focus']};
                background: {colors['field_bg_focus']};
                outline: none;
            }}
            
            #inputFieldTyping::placeholder {{
                color: {colors['placeholder']};
                font-style: italic;
            }}
            """
        }
    

    def get_animated_thinking_style(self, color):
        """Get animated thinking style with specific color."""
        colors = self.get_theme_colors()
        return f"""
        QLineEdit#inputFieldThinking {{
            background: {colors['field_bg']};
            border: 3px solid {color};
            border-radius: 20px;
            padding: 15px 20px;
            font-size: 16px;
            color: {colors['text_color']};
            font-weight: 400;
        }}
        
        QLineEdit#inputFieldThinking:focus {{
            border: 3px solid {color};
            background: {colors['field_bg_focus']};
            outline: none;
        }}
        """
    
    def get_button_styles(self):
        """Get main application button styles."""
        colors = self.get_theme_colors()
        return f"""
        #settingsButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['primary']}, stop:1 #3b82f6);
            border: none;
            border-radius: 25px;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }}
        
        #settingsButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6, stop:1 #2563eb);
        }}
        
        #settingsButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563eb, stop:1 #1d4ed8);
        }}
        
        #copyButton {{
            background: {colors['transparent_white']};
            border: 1px solid rgba(79, 156, 249, 0.3);
            border-radius: 8px;
            color: {colors['primary']};
            font-size: 16px;
            padding: 2px;
        }}
        
        #copyButton:hover {{
            background: rgba(79, 156, 249, 0.1);
            border: 1px solid rgba(79, 156, 249, 0.5);
        }}
        """
    
    
    def get_response_area_style(self):
        """Get response area styles."""
        colors = self.get_theme_colors()
        return f"""
        #responseArea {{
            background: {colors['response_bg']};
            border: 1px solid rgba(79, 156, 249, 0.2);
            border-radius: 15px;
            padding: 20px;
            font-size: 14px;
            line-height: 1.6;
            color: {colors['text_color']};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        #responseArea:focus {{
            outline: none;
        }}
        """
    
    def get_complete_style(self, theme=None):
        """Get the complete stylesheet for main application."""
        if theme and theme != self.current_theme:
            old_theme = self.current_theme
            self.set_theme(theme)
            style = (
                self._get_main_style() +
                self._get_input_field_style()['normal'] +
                self._get_input_field_style()['typing'] +
                self.get_button_styles() +
                self.get_response_area_style()
            )
            self.current_theme = old_theme
            return style
        
        return (
            self._get_main_style() +
            self._get_input_field_style()['normal'] +
            self._get_input_field_style()['typing'] +
            self.get_button_styles() +
            self.get_response_area_style()
        )

    class ButtonStyles:
        """Additional button style utilities."""
        
        def __init__(self, parent_instance):
            self.parent = parent_instance

        def get_primary_button(self):
            colors = self.parent.get_theme_colors()
            return f"""
            QPushButton {{
                background: {colors['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: #3b82f6;
            }}
            """
        
        def get_copy_button_default_style(self):
            colors = self.parent.get_theme_colors()
            return f"""
            QPushButton {{
                background: {colors['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: #3b82f6;
            }}
            """
        
        def get_copy_button_success_style(self):
            """Get success style for copy button."""
            colors = self.parent.get_theme_colors()
            return f"""
            QPushButton {{
                background: {colors['success']};
                color: {colors['white']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            """