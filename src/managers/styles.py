from utils.constants import BackgroundColors


class StyleManager:
    """Manages all UI styles for the application."""
    def __init__(self):
        self.colors = {
            'primary': '#4F9CF9',
            'secondary': '#8B5CF6', 
            'success': '#22C55E',
            'error': '#EF4444',
            'warning': '#F97316',
            'pink': '#EC4899',
            'white': '#FFFFFF',
            'dark': '#2D3142',
            'transparent_white': 'rgba(255, 255, 255, 0.8)',
            'dark_bg_start': '#2d3142',
            'dark_bg_end': '#1a1d29',
            'field_bg': '#374151',
            'field_bg_focus': '#4b5563',
            'border_normal': '#4a5568',
            'border_focus': '#4f9cf9',
            'placeholder': '#9ca3af'
        }
        self.button_styles = self.ButtonStyles(self)

    # === SETTINGS DIALOG STYLES ===
    def get_settings_dialog_styles(self):
        """Get complete styles for settings dialog."""
        return f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.colors['dark_bg_start']}, stop:1 {self.colors['dark_bg_end']});
            }}
            
            #titleLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {self.colors['white']};
                margin-bottom: 10px;
            }}
            
            #fieldLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {self.colors['white']};
                margin-bottom: 5px;
            }}
            
            #settingsInputField {{
                padding: 12px 16px;
                border: 2px solid {self.colors['border_normal']};
                border-radius: 12px;
                font-size: 14px;
                background: {self.colors['field_bg']};
                color: {self.colors['white']};
                min-height: 20px;
            }}
            
            #settingsInputField:focus {{
                border: 2px solid {self.colors['border_focus']};
                outline: none;
                background: {self.colors['field_bg_focus']};
            }}
            
            #settingsInputField::placeholder {{
                color: {self.colors['placeholder']};
            }}
            
            {self._get_settings_button_styles()}
        """

    def _get_settings_button_styles(self):
        """Get button styles for settings dialog."""
        return f"""
            #saveButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.colors['primary']}, stop:1 #3b82f6);
                color: {self.colors['white']};
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
                background: #4b5563;
                color: {self.colors['white']};
                border: 2px solid #6b7280;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }}
            
            #cancelButton:hover {{
                background: #6b7280;
                color: {self.colors['white']};
            }}
        """

    # === MAIN APPLICATION STYLES ===
    
    def _get_main_style(self):
        """Get the main application stylesheet."""
        return f"""
        QMainWindow {{
            background: transparent;
        }}
        #mainContainer {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {BackgroundColors.WINDOW_TOP},
                stop:1 {BackgroundColors.WINDOW_BOTTOM});
            border-radius: 25px;
            border: 1px solid {BackgroundColors.WINDOW_BORDER};
        }}
        """
    
    
    def _get_input_field_style(self):
        """Get input field styles for different states."""
        return {
            'normal': f"""
                #inputField {{
                    background: {BackgroundColors.INPUT_COLOR_BACKGROUND};
                    border: 2px solid {BackgroundColors.INPUT_BORDER_NORMAL};
                    border-radius: 20px;
                    padding: 15px 20px;
                    font-size: 16px;
                    color: #2d3142;
                    font-weight: 400;
                }}
                #inputField:focus {{
                    border: 2px solid {BackgroundColors.INPUT_COLOR_BORDER_FOCUS};
                    background: {BackgroundColors.INPUT_COLOR_BACKGROUND_FOCUS};
                    outline: none;
                }}
                #inputField::placeholder {{
                    color: rgba(45, 49, 66, 0.5);
                    font-style: italic;
                }}
            """,
            'typing': f"""
                #inputFieldTyping {{
                    background: {BackgroundColors.INPUT_COLOR_BACKGROUND};
                    border: 2px solid {BackgroundColors.INPUT_BORDER_COLOR_TYPING};
                    border-radius: 20px;
                    padding: 15px 20px;
                    font-size: 16px;
                    color: #2d3142;
                    font-weight: 400;
                }}
                #inputFieldTyping:focus {{
                    border: 2px solid {BackgroundColors.INPUT_COLOR_BORDER_FOCUS};
                    background: {BackgroundColors.INPUT_COLOR_BACKGROUND_FOCUS};
                    outline: none;
                }}
                #inputFieldTyping::placeholder {{
                    color: rgba(45, 49, 66, 0.5);
                    font-style: italic;
                }}
            """
        }
    
    def get_animated_thinking_style(self, color):
        """Get animated thinking style with specific color."""
        return f"""
        QLineEdit#inputFieldThinking {{
            background: rgba(255, 255, 255, 0.8);
            border: 3px solid {color};
            border-radius: 20px;
            padding: 15px 20px;
            font-size: 16px;
            color: #2d3142;
            font-weight: 400;
        }}
        QLineEdit#inputFieldThinking:focus {{
            border: 3px solid {color};
            background: rgba(255, 255, 255, 1);
            outline: none;
        }}
        """
    
    def get_button_styles(self):
        """Get main application button styles."""
        return """
        #settingsButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #4f9cf9, stop:1 #3b82f6);
            border: none;
            border-radius: 25px;
            color: white;
            font-size: 18px;
            font-weight: bold;
        }
        #settingsButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6, stop:1 #2563eb);
        }
        #settingsButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2563eb, stop:1 #1d4ed8);
        }
        #copyButton {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(79, 156, 249, 0.3);
            border-radius: 8px;
            color: #4f9cf9;
            font-size: 16px;
            padding: 2px;
        }
        #copyButton:hover {
            background: rgba(79, 156, 249, 0.1);
            border: 1px solid rgba(79, 156, 249, 0.5);
        }
        """
    
    
    def get_response_area_style(self):
        """Get response area styles."""
        return """
        #responseArea {
            background: rgba(248, 250, 252, 0.9);
            border: 1px solid rgba(79, 156, 249, 0.2);
            border-radius: 15px;
            padding: 20px;
            font-size: 14px;
            line-height: 1.6;
            color: #2d3142;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        #responseArea:focus {
            outline: none;
        }
        """
    
    def get_complete_style(self):
        """Get the complete stylesheet for main application."""
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
            pass
        
        def get_primary_button(self):
            return """
            QPushButton {
                background: #4f9cf9;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #3b82f6;
            }
            """
        
        def get_copy_button_default_style(self):
            return """
            QPushButton {
                background: #4f9cf9;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #3b82f6;
            }
            """
        
        def get_copy_button_success_style(self):
            """Get success style for copy button."""
            return f"""
                QPushButton {{
                    background: {self.parent.colors['success']};
                    color: {self.parent.colors['white']};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                }}
            """