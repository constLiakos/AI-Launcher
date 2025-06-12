from utils.constants import Theme

class ThemeColors:
    """
    Get all themes
    """
    @staticmethod
    def get_all_themes():
        """
        Get all available themes
        """
        themes = {
            Theme.CLASSIC: ThemeColors._get_light_theme(),
            Theme.DARK: ThemeColors._get_dark_theme(),
            Theme.NATURE: ThemeColors._get_nature_theme(),
        }
        return themes
    
    @staticmethod
    def _get_light_theme():
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
            # === ADDITIONAL COLORS FOR HARDCODED VALUES ===
            'button_gradient_start': '#4f9cf9',      # For button gradients
            'button_gradient_end': '#3b82f6',
            'button_hover_start': '#3b82f6',
            'button_hover_end': '#2563eb',
            'button_pressed_start': '#2563eb',
            'button_pressed_end': '#1d4ed8',
            'stt_recording_end': '#ef5350',          # STT button recording state
            'stt_recording_hover_end': '#d32f2f',
            'message_user_border': '#007bff',        # History conversation styles
            'message_assistant_border': '#333333',
            'message_system_border': '#ffcc80',
            'dropdown_arrow_color': '#374151',       # For combo box down arrow
            'combobox_selection_bg': '#e0f2fe',      # For combobox item selection
            'combobox_item_hover': '#f0f9ff',        # For combobox item hover
        }
    
    @staticmethod
    def _get_dark_theme():
        """Dark theme with blue accents."""
        return {
            # === BRAND COLORS ===
            'brand_primary': "#4F9CF9",
            'brand_primary_hover': "#5CA1F7",
            'brand_primary_active': "#6DABF8",
            'brand_secondary': '#8B5CF6',
            'brand_accent': '#EC4899',
            # === SEMANTIC COLORS ===
            'semantic_success': '#22C55E',
            'semantic_warning': '#F97316',
            'semantic_warning_bg': '#3d2f10',
            'semantic_error': '#EF4444',
            'semantic_info': '#4F9CF9',
            # === TEXT COLORS ===
            'text_primary': '#ffffff',
            'text_secondary': '#d1d5db',
            'text_muted': '#9ca3af',
            'text_placeholder': '#9ca3af',
            'text_inverse': '#2d3142',
            'text_thinking': "#6b7280",
            'text_tertiary': '#9ca3af',
            'text_on_primary': '#ffffff',
            'text_on_secondary': '#ffffff',
            # === BACKGROUND COLORS ===
            'bg_primary': '#2d3142',
            'bg_secondary': '#252836',
            'bg_tertiary': '#1a1d29',
            'bg_elevated': 'rgba(37, 40, 54, 0.9)',
            'bg_overlay': 'rgba(26, 29, 41, 0.8)',
            'bg_window_start': '#2d3142',
            'bg_window_end': '#1a1d29',
            'bg_dialog_start': '#2d3142',
            'bg_dialog_end': '#1a1d29',
            'bg_conversation': 'rgba(37, 40, 54, 0.9)',
            # === MAIN APP INPUT COLORS ===
            'main_input_bg': '#374151',
            'main_input_bg_focus': '#4b5563',
            'main_input_border': '#4a5568',
            'main_input_border_focus': '#4f9cf9',
            # === SETTINGS INPUT COLORS ===
            'settings_input_bg': '#374151',
            'settings_input_bg_focus': '#4b5563',
            'settings_input_border': '#4a5568',
            'settings_input_border_focus': '#4f9cf9',
            # === BUTTON COLORS ===
            'button_primary_bg': "#4F9CF9",
            'button_primary_hover': "#5CA1F7",
            'button_primary_active': "#6DABF8",
            'button_secondary_bg': '#4b5563',
            'button_secondary_hover': '#374151',
            'button_secondary_active': '#2d3142',
            'button_tertiary_bg': 'rgba(79, 156, 249, 0.2)',
            'button_tertiarty_border': 'rgba(79, 156, 249, 0.4)',
            'button_tertiarty_hover_bg': 'rgba(79, 156, 249, 0.3)',
            'button_tertiarty_hover_border': 'rgba(79, 156, 249, 0.6)',
            # === STATE COLORS ===
            'state_recording': "#f8baba",
            'state_recording_hover': "#eea2a2",
            'state_active': "#4F9CF9",
            'state_inactive': '#6b7280',
            # === COMPONENT SPECIFIC ===
            'history_accent': "#4F9CF9",
            'history_message_bg': "#374151",
            'conversation_border': 'rgba(79, 156, 249, 0.3)',
            'scrollbar_track': 'transparent',
            'scrollbar_thumb': 'rgba(79, 156, 249, 0.4)',
            'scrollbar_thumb_hover': 'rgba(79, 156, 249, 0.6)',
            # === SURFACE ALIASES ===
            'surface_primary': '#2d3142',
            'surface_secondary': '#252836',
            'surface_tertiary': '#1a1d29',
            'surface_elevated': 'rgba(37, 40, 54, 0.9)',
            'surface_overlay': 'rgba(26, 29, 41, 0.8)',
            # === BORDER COLORS ===
            'border_subtle': 'rgba(79, 156, 249, 0.25)',
            'border_soft': 'rgba(74, 85, 104, 0.8)',
            'border_default': '#4a5568',
            'border_focus': '#4f9cf9',
            # === CONTAINER BORDERS ===
            'container_border': 'rgba(79, 156, 249, 0.2)',
            'dialog_border': 'rgba(74, 85, 104, 0.6)',
            'surface_border': 'rgba(74, 85, 104, 0.3)',
            # === ADDITIONAL COLORS FOR HARDCODED VALUES ===
            'button_gradient_start': '#4f9cf9',      # For button gradients
            'button_gradient_end': '#3b82f6',
            'button_hover_start': '#5ca1f7',
            'button_hover_end': '#4f9cf9',
            'button_pressed_start': '#6dabf8',
            'button_pressed_end': '#5ca1f7',
            'stt_recording_end': '#ef4444',          # STT button recording state
            'stt_recording_hover_end': '#dc2626',
            'message_user_border': '#4f9cf9',        # History conversation styles
            'message_assistant_border': '#6b7280',
            'message_system_border': '#f59e0b',
            'dropdown_arrow_color': '#d1d5db',       # For combo box down arrow
            'combobox_selection_bg': '#374151',      # For combobox item selection
            'combobox_item_hover': '#4b5563',        # For combobox item hover
        }
    
    @staticmethod
    def _get_nature_theme():
        """Nature-inspired theme with earthy greens and warm accents."""
        return {
            # === BRAND COLORS ===
            'brand_primary': "#4CAF50",
            'brand_primary_hover': "#3E9142",
            'brand_primary_active': "#2E7D32",
            'brand_secondary': '#8D6E63',
            'brand_accent': '#FF7043',
            # === SEMANTIC COLORS ===
            'semantic_success': '#66BB6A',
            'semantic_warning': '#F9A825',
            'semantic_warning_bg': '#FFF8E1',
            'semantic_error': '#E57373',
            'semantic_info': '#4DB6AC',
            # === TEXT COLORS ===
            'text_primary': '#33403C',
            'text_secondary': '#5D6B66',
            'text_muted': '#8A9992',
            'text_placeholder': '#8A9992',
            'text_inverse': '#ffffff',
            'text_thinking': "#A5B1AA",
            'text_tertiary': '#8A9992',
            'text_on_primary': '#ffffff',
            'text_on_secondary': '#33403C',     
            # === BACKGROUND COLORS ===
            'bg_primary': '#FAFBF8',
            'bg_secondary': '#F1F4F0',
            'bg_tertiary': '#E8EDE6',
            'bg_elevated': 'rgba(241, 244, 240, 0.9)',
            'bg_overlay': 'rgba(250, 251, 248, 0.8)',
            'bg_window_start': '#F1F4F0',
            'bg_window_end': '#E0E6DC',
            'bg_dialog_start': '#F1F4F0',
            'bg_dialog_end': '#E0E6DC',
            'bg_conversation': 'rgba(241, 244, 240, 0.9)',
            # === MAIN APP INPUT COLORS ===
            'main_input_bg': '#FAFBF8',
            'main_input_bg_focus': '#FAFBF8',
            'main_input_border': '#C9D6C2',
            'main_input_border_focus': '#4CAF50',
            # === SETTINGS INPUT COLORS ===
            'settings_input_bg': '#FAFBF8',
            'settings_input_bg_focus': '#FAFBF8',
            'settings_input_border': '#C9D6C2',
            'settings_input_border_focus': '#4CAF50',
            # === BUTTON COLORS ===
            'button_primary_bg': "#4CAF50",
            'button_primary_hover': "#3E9142",
            'button_primary_active': "#2E7D32",
            'button_secondary_bg': '#E8EDE6',
            'button_secondary_hover': '#D1DBCB',
            'button_secondary_active': '#B9C7B0',
            'button_tertiary_bg': 'rgba(250, 251, 248, 0.4)',
            'button_tertiarty_border': 'rgba(76, 175, 80, 0.3)',
            'button_tertiarty_hover_bg': 'rgba(76, 175, 80, 0.1)',
            'button_tertiarty_hover_border': 'rgba(76, 175, 80, 0.5)',
            # === STATE COLORS ===
            'state_recording': "#E57373",
            'state_recording_hover': "#EF5350",
            'state_active': "#4CAF50",
            'state_inactive': '#8A9992',
            # === COMPONENT SPECIFIC ===
            'history_accent': "#4CAF50",
            'history_message_bg': "#ECF2E9",
            'conversation_border': 'rgba(76, 175, 80, 0.2)',
            'scrollbar_track': 'transparent',
            'scrollbar_thumb': 'rgba(76, 175, 80, 0.3)',
            'scrollbar_thumb_hover': 'rgba(76, 175, 80, 0.5)',
            # === SURFACE ALIASES ===
            'surface_primary': '#FAFBF8',
            'surface_secondary': '#F1F4F0',
            'surface_tertiary': '#E8EDE6',
            'surface_elevated': 'rgba(241, 244, 240, 0.9)',
            'surface_overlay': 'rgba(250, 251, 248, 0.8)',
            # === BORDER COLORS ===
            'border_subtle': 'rgba(76, 175, 80, 0.15)',
            'border_soft': 'rgba(201, 214, 194, 0.8)',
            'border_default': '#C9D6C2',
            'border_focus': '#4CAF50',
            # === CONTAINER BORDERS ===
            'container_border': 'rgba(76, 175, 80, 0.12)',
            'dialog_border': 'rgba(201, 214, 194, 0.6)',
            'surface_border': 'rgba(156, 175, 149, 0.2)',
            # === ADDITIONAL COLORS FOR HARDCODED VALUES ===
            'button_gradient_start': '#4CAF50',      # For button gradients
            'button_gradient_end': '#2E7D32',
            'button_hover_start': '#3E9142',
            'button_hover_end': '#2E7D32',
            'button_pressed_start': '#2E7D32',
            'button_pressed_end': '#1B5E20',
            'stt_recording_end': '#E57373',          # STT button recording state
            'stt_recording_hover_end': '#EF5350',
            'message_user_border': '#4CAF50',        # History conversation styles
            'message_assistant_border': '#8D6E63',
            'message_system_border': '#FF7043',
            'dropdown_arrow_color': '#5D6B66',       # For combo box down arrow
            'combobox_selection_bg': '#E8F5E8',      # For combobox item selection
            'combobox_item_hover': '#F1F8F1',        # For combobox item hover
        }