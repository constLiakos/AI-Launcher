export enum ThemeType {
    CLASSIC = 'Classic',
    DARK = 'Dark',
    NATURE = 'Nature',
    ROSE = 'Rose',
    HUAWEI = 'Huawei'
}

export interface ThemeColors {
    // === BRAND COLORS ===
    brand_primary: string;
    brand_primary_hover: string;
    brand_primary_active: string;
    brand_secondary: string;
    brand_accent: string;

    // === SEMANTIC COLORS ===
    semantic_success: string;
    semantic_warning: string;
    semantic_warning_bg: string;
    semantic_error: string;
    semantic_info: string;

    // === TEXT COLORS ===
    text_primary: string;
    text_secondary: string;
    text_muted: string;
    text_placeholder: string;
    text_inverse: string;
    text_thinking: string;
    text_tertiary: string;
    text_on_item_hover: string;
    text_on_primary: string;
    text_on_secondary: string;

    // === BACKGROUND COLORS ===
    bg_primary: string;
    bg_secondary: string;
    bg_tertiary: string;
    bg_elevated: string;
    bg_overlay: string;
    bg_window_start: string;
    bg_window_end: string;
    bg_conversation: string;

    // === MAIN APP INPUT COLORS ===
    main_input_bg: string;
    main_input_bg_focus: string;
    main_input_border: string;
    main_input_border_focus: string;

    // === SETTINGS INPUT COLORS ===
    settings_input_bg: string;
    settings_input_bg_focus: string;
    settings_input_border: string;
    settings_input_border_focus: string;

    // === BUTTON COLORS ===
    button_primary_bg: string;
    button_primary_hover: string;
    button_primary_active: string;
    button_secondary_bg: string;
    button_secondary_hover: string;
    button_secondary_active: string;
    button_tertiary_bg: string;
    button_tertiarty_border: string;
    button_tertiarty_hover_bg: string;
    button_tertiarty_hover_border: string;

    // === STATE COLORS ===
    state_recording: string;
    state_recording_hover: string;
    state_active: string;
    state_inactive: string;

    // === COMPONENT SPECIFIC ===
    history_accent: string;
    history_message_bg: string;
    conversation_border: string;
    scrollbar_track: string;
    scrollbar_thumb: string;
    scrollbar_thumb_hover: string;

    // === SURFACE ALIASES ===
    surface_primary: string;
    surface_secondary: string;
    surface_tertiary: string;
    surface_elevated: string;
    surface_overlay: string;

    // === BORDER COLORS ===
    border_subtle: string;
    border_soft: string;
    border_default: string;
    border_focus: string;
    container_border: string;
    dialog_border: string;
    surface_border: string;

    // === ADDITIONAL COLORS ===
    button_gradient_start: string;
    button_gradient_end: string;
    button_hover_start: string;
    button_hover_end: string;
    button_pressed_start: string;
    button_pressed_end: string;
    stt_recording_end: string;
    stt_recording_hover_end: string;
    message_user_border: string;
    message_assistant_border: string;
    message_system_border: string;
    dropdown_arrow_color: string;
    combobox_selection_bg: string;
    combobox_item_hover: string;
}

// =============================================================================
// THEME DEFINITIONS
// =============================================================================

export const getLightTheme = (): ThemeColors => ({
    // === BRAND COLORS ===
    brand_primary: '#5CA1F7',
    brand_primary_hover: '#4A8AE8',
    brand_primary_active: '#3b82f6',
    brand_secondary: '#8B5CF6',
    brand_accent: '#EC4899',

    // === SEMANTIC COLORS ===
    semantic_success: '#22C55E',
    semantic_warning: '#856404',
    semantic_warning_bg: '#fff3cd',
    semantic_error: '#EF4444',
    semantic_info: '#3B82F6',

    // === TEXT COLORS ===
    text_primary: '#2d3142',
    text_secondary: '#6b7280',
    text_muted: '#9ca3af',
    text_placeholder: '#9ca3af',
    text_inverse: '#ffffff',
    text_thinking: '#c6c7cf',
    text_tertiary: '#9ca3af',
    text_on_item_hover: '#ffffff',
    text_on_primary: '#ffffff',
    text_on_secondary: '#374151',

    // === BACKGROUND COLORS ===
    bg_primary: 'rgba(255, 255, 255, 0.35)',
    bg_secondary: '#f8fafc',
    bg_tertiary: '#f3f4f6',
    bg_elevated: 'rgba(248, 250, 252, 0.9)',
    bg_overlay: 'rgba(255, 255, 255, 0.8)',
    bg_window_start: '#f8fafc',
    bg_window_end: '#e2e8f0',
    bg_conversation: 'rgba(248, 250, 252, 0.9)',

    // === MAIN APP INPUT COLORS ===
    main_input_bg: '#ffffff',
    main_input_bg_focus: '#ffffff',
    main_input_border: '#d1d5db',
    main_input_border_focus: '#4f9cf9',

    // === SETTINGS INPUT COLORS ===
    settings_input_bg: '#ffffff',
    settings_input_bg_focus: '#ffffff',
    settings_input_border: '#d1d5db',
    settings_input_border_focus: '#4f9cf9',

    // === BUTTON COLORS ===
    button_primary_bg: '#5CA1F7',
    button_primary_hover: '#4A8AE8',
    button_primary_active: '#3b82f6',
    button_secondary_bg: '#f3f4f6',
    button_secondary_hover: '#d1d5db',
    button_secondary_active: '#9ca3af',
    button_tertiary_bg: 'rgba(255, 255, 255, 0.4)',
    button_tertiarty_border: 'rgba(79, 156, 249, 0.3)',
    button_tertiarty_hover_bg: 'rgba(79, 156, 249, 0.1)',
    button_tertiarty_hover_border: 'rgba(79, 156, 249, 0.5)',

    // === STATE COLORS ===
    state_recording: '#e77c7c',
    state_recording_hover: '#e25a5a',
    state_active: '#5CA1F7',
    state_inactive: '#9ca3af',

    // === COMPONENT SPECIFIC ===
    history_accent: '#5CA1F7',
    history_message_bg: '#ebf0f5',
    conversation_border: 'rgba(79, 156, 249, 0.2)',
    scrollbar_track: 'transparent',
    scrollbar_thumb: 'rgba(79, 156, 249, 0.3)',
    scrollbar_thumb_hover: 'rgba(79, 156, 249, 0.5)',

    // === SURFACE ALIASES ===
    surface_primary: '#ffffff',
    surface_secondary: '#f8fafc',
    surface_tertiary: '#f3f4f6',
    surface_elevated: 'rgba(248, 250, 252, 0.9)',
    surface_overlay: 'rgba(255, 255, 255, 0.8)',

    // === BORDER COLORS ===
    border_subtle: 'rgba(79, 156, 249, 0.15)',
    border_soft: 'rgba(209, 213, 219, 0.8)',
    border_default: '#d1d5db',
    border_focus: '#4f9cf9',
    container_border: 'rgba(79, 156, 249, 0.12)',
    dialog_border: 'rgba(209, 213, 219, 0.6)',
    surface_border: 'rgba(148, 163, 184, 0.2)',

    // === ADDITIONAL COLORS ===
    button_gradient_start: '#4f9cf9',
    button_gradient_end: '#3b82f6',
    button_hover_start: '#3b82f6',
    button_hover_end: '#2563eb',
    button_pressed_start: '#2563eb',
    button_pressed_end: '#1d4ed8',
    stt_recording_end: '#ef5350',
    stt_recording_hover_end: '#d32f2f',
    message_user_border: '#007bff',
    message_assistant_border: '#333333',
    message_system_border: '#ffcc80',
    dropdown_arrow_color: '#374151',
    combobox_selection_bg: '#e0f2fe',
    combobox_item_hover: '#5da1f5'
});

export const getDarkTheme = (): ThemeColors => ({
    // === BRAND COLORS ===
    brand_primary: '#4F9CF9',
    brand_primary_hover: '#5CA1F7',
    brand_primary_active: '#6DABF8',
    brand_secondary: '#8B5CF6',
    brand_accent: '#EC4899',

    // === SEMANTIC COLORS ===
    semantic_success: '#22C55E',
    semantic_warning: '#F97316',
    semantic_warning_bg: '#3d2f10',
    semantic_error: '#EF4444',
    semantic_info: '#4F9CF9',

    // === TEXT COLORS ===
    text_primary: '#ffffff',
    text_secondary: '#d1d5db',
    text_muted: '#9ca3af',
    text_placeholder: '#9ca3af',
    text_inverse: '#2d3142',
    text_thinking: '#6b7280',
    text_tertiary: '#9ca3af',
    text_on_primary: '#ffffff',
    text_on_secondary: '#ffffff',
    text_on_item_hover: '#1a1d29',

    // === BACKGROUND COLORS ===
    bg_primary: 'rgba(45,49,66, 0.35)',
    bg_secondary: '#252836',
    bg_tertiary: '#1a1d29',
    bg_elevated: 'rgba(37, 40, 54, 0.9)',
    bg_overlay: 'rgba(26, 29, 41, 0.8)',
    bg_window_start: '#2d3142',
    bg_window_end: '#1a1d29',
    bg_conversation: 'rgba(37, 40, 54, 0.9)',

    // === MAIN APP INPUT COLORS ===
    main_input_bg: '#374151',
    main_input_bg_focus: '#4b5563',
    main_input_border: '#4a5568',
    main_input_border_focus: '#4f9cf9',

    // === SETTINGS INPUT COLORS ===
    settings_input_bg: '#374151',
    settings_input_bg_focus: '#4b5563',
    settings_input_border: '#4a5568',
    settings_input_border_focus: '#4f9cf9',

    // === BUTTON COLORS ===
    button_primary_bg: '#4F9CF9',
    button_primary_hover: '#5CA1F7',
    button_primary_active: '#6DABF8',
    button_secondary_bg: '#4b5563',
    button_secondary_hover: '#374151',
    button_secondary_active: '#2d3142',
    button_tertiary_bg: 'rgba(79, 156, 249, 0.2)',
    button_tertiarty_border: 'rgba(79, 156, 249, 0.4)',
    button_tertiarty_hover_bg: 'rgba(79, 156, 249, 0.3)',
    button_tertiarty_hover_border: 'rgba(79, 156, 249, 0.6)',

    // === STATE COLORS ===
    state_recording: '#f8baba',
    state_recording_hover: '#eea2a2',
    state_active: '#4F9CF9',
    state_inactive: '#6b7280',

    // === COMPONENT SPECIFIC ===
    history_accent: '#4F9CF9',
    history_message_bg: '#374151',
    conversation_border: 'rgba(79, 156, 249, 0.3)',
    scrollbar_track: 'transparent',
    scrollbar_thumb: 'rgba(79, 156, 249, 0.4)',
    scrollbar_thumb_hover: 'rgba(79, 156, 249, 0.6)',

    // === SURFACE ALIASES ===
    surface_primary: '#2d3142',
    surface_secondary: '#252836',
    surface_tertiary: '#1a1d29',
    surface_elevated: 'rgba(37, 40, 54, 0.9)',
    surface_overlay: 'rgba(26, 29, 41, 0.8)',

    // === BORDER COLORS ===
    border_subtle: 'rgba(79, 156, 249, 0.25)',
    border_soft: 'rgba(74, 85, 104, 0.8)',
    border_default: '#4a5568',
    border_focus: '#4f9cf9',
    container_border: 'rgba(79, 156, 249, 0.2)',
    dialog_border: 'rgba(74, 85, 104, 0.6)',
    surface_border: 'rgba(74, 85, 104, 0.3)',

    // === ADDITIONAL COLORS ===
    button_gradient_start: '#4f9cf9',
    button_gradient_end: '#3b82f6',
    button_hover_start: '#5ca1f7',
    button_hover_end: '#4f9cf9',
    button_pressed_start: '#6dabf8',
    button_pressed_end: '#5ca1f7',
    stt_recording_end: '#ef4444',
    stt_recording_hover_end: '#dc2626',
    message_user_border: '#4f9cf9',
    message_assistant_border: '#6b7280',
    message_system_border: '#f59e0b',
    dropdown_arrow_color: '#d1d5db',
    combobox_selection_bg: '#374151',
    combobox_item_hover: '#7F95AF'
});

export const getNatureTheme = (): ThemeColors => ({
    // === BRAND COLORS ===
    brand_primary: '#4CAF50',
    brand_primary_hover: '#3E9142',
    brand_primary_active: '#2E7D32',
    brand_secondary: '#8D6E63',
    brand_accent: '#FF7043',

    // === SEMANTIC COLORS ===
    semantic_success: '#66BB6A',
    semantic_warning: '#F9A825',
    semantic_warning_bg: '#FFF8E1',
    semantic_error: '#E57373',
    semantic_info: '#4DB6AC',

    // === TEXT COLORS ===
    text_primary: '#33403C',
    text_secondary: '#5D6B66',
    text_muted: '#8A9992',
    text_placeholder: '#8A9992',
    text_inverse: '#ffffff',
    text_thinking: '#A5B1AA',
    text_tertiary: '#8A9992',
    text_on_primary: '#ffffff',
    text_on_secondary: '#33403C',
    text_on_item_hover: '#ffffff',

    // === BACKGROUND COLORS ===
    bg_primary: 'rgba(250,251,248, 0.35)',
    bg_secondary: '#F1F4F0',
    bg_tertiary: '#E8EDE6',
    bg_elevated: 'rgba(241, 244, 240, 0.9)',
    bg_overlay: 'rgba(250, 251, 248, 0.8)',
    bg_window_start: '#F1F4F0',
    bg_window_end: '#E0E6DC',
    bg_conversation: 'rgba(241, 244, 240, 0.9)',

    // === MAIN APP INPUT COLORS ===
    main_input_bg: '#FAFBF8',
    main_input_bg_focus: '#FAFBF8',
    main_input_border: '#C9D6C2',
    main_input_border_focus: '#4CAF50',

    // === SETTINGS INPUT COLORS ===
    settings_input_bg: '#FAFBF8',
    settings_input_bg_focus: '#FAFBF8',
    settings_input_border: '#C9D6C2',
    settings_input_border_focus: '#4CAF50',

    // === BUTTON COLORS ===
    button_primary_bg: '#4CAF50',
    button_primary_hover: '#3E9142',
    button_primary_active: '#2E7D32',
    button_secondary_bg: '#E8EDE6',
    button_secondary_hover: '#D1DBCB',
    button_secondary_active: '#B9C7B0',
    button_tertiary_bg: 'rgba(250, 251, 248, 0.4)',
    button_tertiarty_border: 'rgba(76, 175, 80, 0.3)',
    button_tertiarty_hover_bg: 'rgba(76, 175, 80, 0.1)',
    button_tertiarty_hover_border: 'rgba(76, 175, 80, 0.5)',

    // === STATE COLORS ===
    state_recording: '#E57373',
    state_recording_hover: '#EF5350',
    state_active: '#4CAF50',
    state_inactive: '#8A9992',

    // === COMPONENT SPECIFIC ===
    history_accent: '#4CAF50',
    history_message_bg: '#ECF2E9',
    conversation_border: 'rgba(76, 175, 80, 0.2)',
    scrollbar_track: 'transparent',
    scrollbar_thumb: 'rgba(76, 175, 80, 0.3)',
    scrollbar_thumb_hover: 'rgba(76, 175, 80, 0.5)',

    // === SURFACE ALIASES ===
    surface_primary: '#FAFBF8',
    surface_secondary: '#F1F4F0',
    surface_tertiary: '#E8EDE6',
    surface_elevated: 'rgba(241, 244, 240, 0.9)',
    surface_overlay: 'rgba(250, 251, 248, 0.8)',

    // === BORDER COLORS ===
    border_subtle: 'rgba(76, 175, 80, 0.15)',
    border_soft: 'rgba(201, 214, 194, 0.8)',
    border_default: '#C9D6C2',
    border_focus: '#4CAF50',
    container_border: 'rgba(76, 175, 80, 0.12)',
    dialog_border: 'rgba(201, 214, 194, 0.6)',
    surface_border: 'rgba(156, 175, 149, 0.2)',

    // === ADDITIONAL COLORS ===
    button_gradient_start: '#4CAF50',
    button_gradient_end: '#2E7D32',
    button_hover_start: '#3E9142',
    button_hover_end: '#2E7D32',
    button_pressed_start: '#2E7D32',
    button_pressed_end: '#1B5E20',
    stt_recording_end: '#E57373',
    stt_recording_hover_end: '#EF5350',
    message_user_border: '#4CAF50',
    message_assistant_border: '#8D6E63',
    message_system_border: '#FF7043',
    dropdown_arrow_color: '#5D6B66',
    combobox_selection_bg: '#E8F5E8',
    combobox_item_hover: '#71C274'
});

export const getRoseTheme = (): ThemeColors => ({
    // === BRAND COLORS ===
    brand_primary: '#FF6B9D',
    brand_primary_hover: '#FF5A8A',
    brand_primary_active: '#E91E63',
    brand_secondary: '#9C27B0',
    brand_accent: '#FF9800',

    // === SEMANTIC COLORS ===
    semantic_success: '#4CAF50',
    semantic_warning: '#FF9800',
    semantic_warning_bg: '#FFF3E0',
    semantic_error: '#F44336',
    semantic_info: '#FF6B9D',

    // === TEXT COLORS ===
    text_primary: '#4A2C3A',
    text_secondary: '#6D4C57',
    text_muted: '#9E7B8A',
    text_placeholder: '#9E7B8A',
    text_inverse: '#ffffff',
    text_thinking: '#B8A1AB',
    text_tertiary: '#9E7B8A',
    text_on_primary: '#ffffff',
    text_on_secondary: '#4A2C3A',
    text_on_item_hover: '#ffffff',

    // === BACKGROUND COLORS ===
    bg_primary: 'rgba(253,248,251, 0.35)',
    bg_secondary: '#F8F0F4',
    bg_tertiary: '#F3E5EA',
    bg_elevated: 'rgba(248, 240, 244, 0.9)',
    bg_overlay: 'rgba(253, 248, 251, 0.8)',
    bg_window_start: '#F8F0F4',
    bg_window_end: '#F0D9E1',
    bg_conversation: 'rgba(248, 240, 244, 0.9)',

    // === MAIN APP INPUT COLORS ===
    main_input_bg: '#FDF8FB',
    main_input_bg_focus: '#FDF8FB',
    main_input_border: '#E8C2D0',
    main_input_border_focus: '#FF6B9D',

    // === SETTINGS INPUT COLORS ===
    settings_input_bg: '#FDF8FB',
    settings_input_bg_focus: '#FDF8FB',
    settings_input_border: '#E8C2D0',
    settings_input_border_focus: '#FF6B9D',

    // === BUTTON COLORS ===
    button_primary_bg: '#FF6B9D',
    button_primary_hover: '#FF5A8A',
    button_primary_active: '#E91E63',
    button_secondary_bg: '#F3E5EA',
    button_secondary_hover: '#E8C2D0',
    button_secondary_active: '#D8A2B8',
    button_tertiary_bg: 'rgba(253, 248, 251, 0.4)',
    button_tertiarty_border: 'rgba(255, 107, 157, 0.3)',
    button_tertiarty_hover_bg: 'rgba(255, 107, 157, 0.1)',
    button_tertiarty_hover_border: 'rgba(255, 107, 157, 0.5)',

    // === STATE COLORS ===
    state_recording: '#FF7043',
    state_recording_hover: '#FF5722',
    state_active: '#FF6B9D',
    state_inactive: '#9E7B8A',

    // === COMPONENT SPECIFIC ===
    history_accent: '#FF6B9D',
    history_message_bg: '#F7ECF0',
    conversation_border: 'rgba(255, 107, 157, 0.2)',
    scrollbar_track: 'transparent',
    scrollbar_thumb: 'rgba(255, 107, 157, 0.3)',
    scrollbar_thumb_hover: 'rgba(255, 107, 157, 0.5)',

    // === SURFACE ALIASES ===
    surface_primary: '#FDF8FB',
    surface_secondary: '#F8F0F4',
    surface_tertiary: '#F3E5EA',
    surface_elevated: 'rgba(248, 240, 244, 0.9)',
    surface_overlay: 'rgba(253, 248, 251, 0.8)',

    // === BORDER COLORS ===
    border_subtle: 'rgba(255, 107, 157, 0.15)',
    border_soft: 'rgba(232, 194, 208, 0.8)',
    border_default: '#E8C2D0',
    border_focus: '#FF6B9D',
    container_border: 'rgba(255, 107, 157, 0.12)',
    dialog_border: 'rgba(232, 194, 208, 0.6)',
    surface_border: 'rgba(216, 162, 184, 0.2)',

    // === ADDITIONAL COLORS ===
    button_gradient_start: '#FF6B9D',
    button_gradient_end: '#E91E63',
    button_hover_start: '#FF5A8A',
    button_hover_end: '#E91E63',
    button_pressed_start: '#E91E63',
    button_pressed_end: '#C2185B',
    stt_recording_end: '#FF7043',
    stt_recording_hover_end: '#FF5722',
    message_user_border: '#FF6B9D',
    message_assistant_border: '#9C27B0',
    message_system_border: '#FF9800',
    dropdown_arrow_color: '#6D4C57',
    combobox_selection_bg: '#F7ECF0',
    combobox_item_hover: '#FA80A9'
});

export const getHuaweiTheme = (): ThemeColors => ({
    // === BRAND COLORS ===
    brand_primary: '#FF8A50',
    brand_primary_hover: '#FF7043',
    brand_primary_active: '#F4511E',
    brand_secondary: '#42A5F5',
    brand_accent: '#66BB6A',

    // === SEMANTIC COLORS ===
    semantic_success: '#4CAF50',
    semantic_warning: '#FFB74D',
    semantic_warning_bg: '#FFF8E1',
    semantic_error: '#FF7043',
    semantic_info: '#29B6F6',

    // === TEXT COLORS ===
    text_primary: '#2E3B2E',
    text_secondary: '#455A64',
    text_muted: '#78909C',
    text_placeholder: '#78909C',
    text_inverse: '#ffffff',
    text_thinking: '#90A4AE',
    text_tertiary: '#78909C',
    text_on_primary: '#ffffff',
    text_on_secondary: '#2E3B2E',
    text_on_item_hover: '#2E3B2E',

    // === BACKGROUND COLORS ===
    bg_primary: 'rgba(253, 252, 250, 0.35)',
    bg_secondary: '#FAF3E9',
    bg_tertiary: '#F2F8F2',
    bg_elevated: 'rgba(240, 246, 255, 0.9)',
    bg_overlay: 'rgba(250, 252, 255, 0.8)',
    bg_window_start: '#DFE9F8',
    bg_window_end: '#FFF3E0',
    bg_conversation: 'rgba(252, 255, 255, 0.8)',

    // === MAIN APP INPUT COLORS ===
    main_input_bg: 'rgba(253, 252, 250, 0.5)',
    main_input_bg_focus: 'rgba(253, 252, 248, 0.6)',
    main_input_border: '#C4E0FC',
    main_input_border_focus: '#FF8A50',

    // === SETTINGS INPUT COLORS ===
    settings_input_bg: '#FFFBF0',
    settings_input_bg_focus: '#FFF8E1',
    settings_input_border: '#B3D9FF',
    settings_input_border_focus: '#FF8A50',

    // === BUTTON COLORS ===
    button_primary_bg: '#FF8A50',
    button_primary_hover: '#FF7043',
    button_primary_active: '#F4511E',
    button_secondary_bg: '#81C784',
    button_secondary_hover: '#66BB6A',
    button_secondary_active: '#4CAF50',
    button_tertiary_bg: 'rgba(250, 252, 255, 0.4)',
    button_tertiarty_border: 'rgba(255, 138, 80, 0.3)',
    button_tertiarty_hover_bg: 'rgba(255, 138, 80, 0.1)',
    button_tertiarty_hover_border: 'rgba(255, 138, 80, 0.5)',

    // === STATE COLORS ===
    state_recording: '#FF7043',
    state_recording_hover: '#FF5722',
    state_active: '#FF8A50',
    state_inactive: '#78909C',

    // === COMPONENT SPECIFIC ===
    history_accent: '#FF8A50',
    history_message_bg: '#F0F8FF',
    conversation_border: 'rgba(255, 138, 80, 0.2)',
    scrollbar_track: 'transparent',
    scrollbar_thumb: 'rgba(66, 165, 245, 0.35)',
    scrollbar_thumb_hover: 'rgba(66, 165, 245, 0.5)',

    // === SURFACE ALIASES ===
    surface_primary: '#FAFCFF',
    surface_secondary: '#F0F6FF',
    surface_tertiary: '#F2F8F2',
    surface_elevated: 'rgba(240, 246, 255, 0.9)',
    surface_overlay: 'rgba(250, 252, 255, 0.8)',

    // === BORDER COLORS ===
    border_subtle: 'rgba(66, 165, 245, 0.18)',
    border_soft: 'rgba(179, 217, 255, 0.8)',
    border_default: '#B3D9FF',
    border_focus: '#FF8A50',
    container_border: 'rgba(102, 187, 106, 0.15)',
    dialog_border: 'rgba(179, 217, 255, 0.6)',
    surface_border: 'rgba(144, 202, 249, 0.25)',

    // === ADDITIONAL COLORS ===
    button_gradient_start: '#FF8A50',
    button_gradient_end: '#F4511E',
    button_hover_start: '#FF7043',
    button_hover_end: '#F4511E',
    button_pressed_start: '#F4511E',
    button_pressed_end: '#E64A19',
    stt_recording_end: '#FF7043',
    stt_recording_hover_end: '#FF5722',
    message_user_border: '#FF8A50',
    message_assistant_border: '#42A5F5',
    message_system_border: '#66BB6A',
    dropdown_arrow_color: '#455A64',
    combobox_selection_bg: '#E6F3FF',
    combobox_item_hover: '#81C784'
});
