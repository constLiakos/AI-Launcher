// =============================================================================
// TEXT CONSTANTS
// =============================================================================

export const TEXT = {
  // =============================================================================
  // INPUT & PLACEHOLDERS
  // =============================================================================
  INPUT_PLACEHOLDER: 'Ask AI anything...',
  SEARCH_PLACEHOLDER: 'Search conversations...',
  API_KEY_PLACEHOLDER: 'Enter your API key...',
  SYSTEM_PROMPT_PLACEHOLDER: 'Enter system prompt...',
  
  // =============================================================================
  // BUTTON LABELS
  // =============================================================================
  SETTINGS_BUTTON: '⚙',
  COPY_BUTTON: '📋',
  COPY_SUCCESS: '✓',
  SEND_BUTTON: 'Send',
  CANCEL_BUTTON: 'Cancel',
  SAVE_BUTTON: 'Save',
  DELETE_BUTTON: 'Delete',
  CLEAR_BUTTON: 'Clear',
  NEW_BUTTON: 'New',
  EDIT_BUTTON: 'Edit',
  
  // =============================================================================
  // SYSTEM TRAY
  // =============================================================================
  TRAY_TOOLTIP: 'AI Launcher',
  TRAY_SHOW: 'Show',
  TRAY_HIDE: 'Hide',
  TRAY_SETTINGS: 'Settings',
  TRAY_ABOUT: 'About',
  TRAY_QUIT: 'Quit',
  TRAY_ICON_TEXT: 'AI',
  
  // Tray messages
  TRAY_BACKGROUND_MESSAGE: 'Application is running in the background',
  TRAY_BACKGROUND_TITLE: 'AI Launcher',
  TRAY_NOT_AVAILABLE: 'System tray is not available on this system',
  
  // =============================================================================
  // STATUS MESSAGES
  // =============================================================================
  STATUS_THINKING: 'Thinking... 🤔',
  STATUS_STREAMING: 'Streaming... ⚡',
  STATUS_COMPLETE: '✓ Response complete',
  STATUS_ERROR: 'Error occurred',
  STATUS_READY: 'Ready',
  STATUS_CONNECTING: 'Connecting...',
  STATUS_CONNECTED: 'Connected',
  STATUS_DISCONNECTED: 'Disconnected',
  
  // Clipboard status
  STATUS_NO_TEXT_TO_COPY: 'No text to copy',
  STATUS_COPY_FAILED: 'Copy failed',
  STATUS_COPIED: 'Copied to clipboard',

  // AI Response placeholders
  AI_PLACEHOLDER_RESPONSE: 'This is a placeholder response. AI integration coming soon!',
  AI_THINKING_RESPONSES: [
    'Let me think about that... 🤔',
    'Processing your request... ⚡',
    'Analyzing your question... 🔍',
    'Generating response... ✨'
  ],
  
  // =============================================================================
  // ERROR MESSAGES
  // =============================================================================
  ERROR_PREFIX: '❌ Error: ',
  ERROR_PROCESSING_RESPONSE: 'Error processing response: ',
  ERROR_COPYING_CLIPBOARD: 'Error copying to clipboard: ',
  ERROR_CANCELLING_REQUEST: 'Error cancelling API request: ',
  ERROR_CHUNK_HANDLING: 'Error handling chunk: ',
  ERROR_NETWORK: 'Network error occurred',
  ERROR_API_KEY: 'Invalid API key',
  ERROR_API_LIMIT: 'API rate limit exceeded',
  ERROR_UNKNOWN: 'An unknown error occurred',
  
  // =============================================================================
  // SUCCESS MESSAGES
  // =============================================================================
  SUCCESS_PREFIX: '✅ Success: ',
  SUCCESS_MESSAGE_SENT: 'Message sent successfully',
  SUCCESS_CONVERSATION_CREATED: 'New conversation created',
  SUCCESS_CONVERSATION_DELETED: 'Conversation deleted',
  SUCCESS_SETTINGS_SAVED: 'Settings saved successfully',
  SUCCESS_BACKUP_CREATED: 'Backup created successfully',
  SUCCESS_DATA_IMPORTED: 'Data imported successfully',
  
  // =============================================================================
  // CONVERSATION & MESSAGES
  // =============================================================================
  CONVERSATION_DEFAULT_TITLE: 'New Conversation',
  CONVERSATION_EMPTY_STATE: 'Start a conversation by typing a message above',
  CONVERSATION_LOADING: 'Loading conversation...',
  CONVERSATION_NO_MESSAGES: 'No messages yet',
  
  MESSAGE_USER_LABEL: 'You',
  MESSAGE_ASSISTANT_LABEL: 'AI Assistant',
  MESSAGE_SYSTEM_LABEL: 'System',
  MESSAGE_DELETED: '[Message deleted]',
  MESSAGE_EDIT_PLACEHOLDER: 'Edit your message...',
  
  // =============================================================================
  // SETTINGS DIALOG
  // =============================================================================
  SETTINGS_TITLE: 'AI Launcher Settings',
  SETTINGS_TAB_GENERAL: 'General',
  SETTINGS_TAB_API: 'API',
  SETTINGS_TAB_HOTKEYS: 'Hotkeys',
  SETTINGS_TAB_APPEARANCE: 'Appearance',
  SETTINGS_TAB_ADVANCED: 'Advanced',
  
  // API Settings
  SETTINGS_API_KEY_LABEL: 'API Key:',
  SETTINGS_API_BASE_LABEL: 'API Base URL:',
  SETTINGS_API_MODEL_LABEL: 'Model:',
  SETTINGS_API_TIMEOUT_LABEL: 'Request Timeout (seconds):',
  SETTINGS_API_TEMPERATURE_LABEL: 'Temperature:',
  SETTINGS_API_MAX_TOKENS_LABEL: 'Max Tokens:',
  SETTINGS_SYSTEM_PROMPT_LABEL: 'System Prompt:',
  
  // Hotkey Settings
  SETTINGS_HOTKEY_GLOBAL_TOGGLE_LABEL: 'Toggle Window:',
  SETTINGS_HOTKEY_STT_LABEL: 'Voice Recording:',
  SETTINGS_HOTKEY_SETTINGS_LABEL: 'Open Settings:',
  
  // General Settings
  SETTINGS_THEME_LABEL: 'Theme:',
  SETTINGS_STARTUP_LABEL: 'Start with system',
  SETTINGS_MINIMIZE_TO_TRAY_LABEL: 'Minimize to system tray',
  SETTINGS_CLOSE_TO_TRAY_LABEL: 'Close to system tray',
  SETTINGS_SHOW_NOTIFICATIONS_LABEL: 'Show notifications',
  
  // Conversation Settings
  SETTINGS_CLEAR_ON_MINIMIZE_LABEL: 'Clear conversation on minimize',
  SETTINGS_HISTORY_LIMIT_LABEL: 'Conversation history limit:',
  SETTINGS_AUTO_TITLE_LABEL: 'Auto-generate conversation titles',
  
  // =============================================================================
  // ABOUT DIALOG
  // =============================================================================
  ABOUT_TITLE: 'About AI Launcher',
  ABOUT_VERSION: 'Version',
  ABOUT_DESCRIPTION: 'A lightweight desktop AI assistant with system tray integration',
  ABOUT_AUTHOR: 'Author',
  ABOUT_LICENSE: 'License',
  ABOUT_WEBSITE: 'Website',
  ABOUT_GITHUB: 'GitHub Repository',
  ABOUT_SUPPORT: 'Support',
  
  ABOUT_TEXT: `
    <h3>🚀 AI Launcher</h3>
    <p>🖥️ A modern, lightweight desktop AI assistant with a sleek system tray interface offering quick access to AI conversations via global hotkeys ⌨️ and real-time streaming responses ⏳.</p>
    <h4>🛠️ Technologies:</h4>
    <ul>
      <li>⚡ Electron</li>
      <li>🎨 TypeScript</li>
      <li>🤖 OpenAI-compatible APIs</li>
      <li>🗄️ SQLite Database</li>
    </ul>
  `,
  
  // =============================================================================
  // TOOLTIPS & HELP
  // =============================================================================
  TOOLTIP_TOGGLE_INPUT_MODE: 'Switch between single/multi-line input (Tab)',
  TOOLTIP_START_RECORDING: 'Start voice recording (F2)',
  TOOLTIP_STOP_RECORDING: 'Stop voice recording (F2)',
  TOOLTIP_OPEN_SETTINGS: 'Open settings (Ctrl+S)',
  TOOLTIP_EXPAND_CONVERSATION: 'Show conversation history (F4)',
  TOOLTIP_NEW_CONVERSATION: 'Start new conversation (Ctrl+N)',
  TOOLTIP_CLEAR_CONVERSATION: 'Clear current conversation',
  TOOLTIP_COPY_MESSAGE: 'Copy message to clipboard',
  TOOLTIP_EDIT_MESSAGE: 'Edit this message',
  TOOLTIP_DELETE_MESSAGE: 'Delete this message',
  TOOLTIP_REGENERATE_RESPONSE: 'Regenerate AI response',
  
  // =============================================================================
  // RECORDING & STT
  // =============================================================================
  RECORDING_PREPARING: 'Preparing microphone...',
  RECORDING_LISTENING: 'Listening... 🎤',
  RECORDING_PROCESSING: 'Processing audio...',
  RECORDING_COMPLETE: 'Recording complete',
  RECORDING_ERROR: 'Recording error occurred',
  RECORDING_NO_PERMISSION: 'Microphone permission required',
  RECORDING_NOT_SUPPORTED: 'Recording not supported in this browser',
  
  STT_BUTTON_START: 'Start Recording',
  STT_BUTTON_STOP: 'Stop Recording',
  STT_BUTTON_PROCESSING: 'Processing...',
  
  // =============================================================================
  // KEYBOARD SHORTCUTS
  // =============================================================================
  SHORTCUT_SEND_MESSAGE: 'Press Enter to send, Shift+Enter for new line',
  SHORTCUT_MULTILINE_SEND: 'Press Ctrl+Enter to send',
  SHORTCUT_ESCAPE_HIDE: 'Press Escape to hide window',
  SHORTCUT_TAB_TOGGLE: 'Press Tab to toggle input mode',
  
  // =============================================================================
  // VALIDATION MESSAGES
  // =============================================================================
  VALIDATION_REQUIRED: 'This field is required',
  VALIDATION_INVALID_URL: 'Please enter a valid URL',
  VALIDATION_INVALID_NUMBER: 'Please enter a valid number',
  VALIDATION_MIN_LENGTH: 'Minimum length is {min} characters',
  VALIDATION_MAX_LENGTH: 'Maximum length is {max} characters',
  VALIDATION_INVALID_HOTKEY: 'Invalid hotkey combination',
  VALIDATION_HOTKEY_CONFLICT: 'This hotkey is already assigned',
  
  // =============================================================================
  // LOADING STATES
  // =============================================================================
  LOADING_CONVERSATIONS: 'Loading conversations...',
  LOADING_MESSAGES: 'Loading messages...',
  LOADING_SETTINGS: 'Loading settings...',
  LOADING_MODELS: 'Loading available models...',
  LOADING_GENERAL: 'Loading...',
  
  // =============================================================================
  // CONFIRMATION DIALOGS
  // =============================================================================
  CONFIRM_DELETE_CONVERSATION: 'Are you sure you want to delete this conversation?',
  CONFIRM_CLEAR_ALL_CONVERSATIONS: 'Are you sure you want to clear all conversations?',
  CONFIRM_DELETE_MESSAGE: 'Are you sure you want to delete this message?',
  CONFIRM_RESET_SETTINGS: 'Are you sure you want to reset all settings to default?',
  CONFIRM_QUIT_APP: 'Are you sure you want to quit AI Launcher?',
  
  CONFIRM_YES: 'Yes',
  CONFIRM_NO: 'No',
  CONFIRM_OK: 'OK',
  CONFIRM_CANCEL: 'Cancel',
  
  // =============================================================================
  // MENU ITEMS
  // =============================================================================
  MENU_FILE: 'File',
  MENU_EDIT: 'Edit',
  MENU_VIEW: 'View',
  MENU_HELP: 'Help',
  
  MENU_NEW_CONVERSATION: 'New Conversation',
  MENU_OPEN_SETTINGS: 'Settings',
  MENU_EXPORT_CONVERSATION: 'Export Conversation',
  MENU_IMPORT_CONVERSATION: 'Import Conversation',
  MENU_QUIT: 'Quit',
  
  MENU_COPY: 'Copy',
  MENU_PASTE: 'Paste',
  MENU_SELECT_ALL: 'Select All',
  MENU_FIND: 'Find',
  
  MENU_TOGGLE_WINDOW: 'Toggle Window',
  MENU_ALWAYS_ON_TOP: 'Always on Top',
  MENU_FULLSCREEN: 'Fullscreen',
  
  MENU_ABOUT: 'About AI Launcher',
  MENU_DOCUMENTATION: 'Documentation',
  MENU_REPORT_BUG: 'Report Bug',
  MENU_CHECK_UPDATES: 'Check for Updates',
  
  // =============================================================================
  // INPUT MODES
  // =============================================================================
  INPUT_MODE_SINGLE: 'Single Line',
  INPUT_MODE_MULTI: 'Multi Line',
  
  // =============================================================================
  // WINDOW STATES
  // =============================================================================
  WINDOW_STATE_COMPACT: 'Compact Mode',
  WINDOW_STATE_EXPANDED: 'Expanded Mode',
  
  // =============================================================================
  // THEMES
  // =============================================================================
  THEME_CLASSIC: 'Classic',
  THEME_DARK: 'Dark',
  THEME_NATURE: 'Nature',
  THEME_ROSE: 'Rose',
  THEME_HUAWEI: 'Huawei',
  
  // =============================================================================
  // TIME & DATES
  // =============================================================================
  TIME_NOW: 'now',
  TIME_MINUTE_AGO: '1 minute ago',
  TIME_MINUTES_AGO: '{minutes} minutes ago',
  TIME_HOUR_AGO: '1 hour ago',
  TIME_HOURS_AGO: '{hours} hours ago',
  TIME_TODAY: 'Today',
  TIME_YESTERDAY: 'Yesterday',
  TIME_DAYS_AGO: '{days} days ago',
  
  // =============================================================================
  // UNITS & FORMATTING
  // =============================================================================
  UNIT_CHARACTERS: 'characters',
  UNIT_WORDS: 'words',
  UNIT_MESSAGES: 'messages',
  UNIT_CONVERSATIONS: 'conversations',
  UNIT_BYTES: 'bytes',
  UNIT_KB: 'KB',
  UNIT_MB: 'MB',
  UNIT_GB: 'GB'
} as const;

export const getRandomThinkingMessage = (): string => {
  const messages = TEXT.AI_THINKING_RESPONSES;
  return messages[Math.floor(Math.random() * messages.length)];
};

// =============================================================================
// TEXT UTILITIES
// =============================================================================

/**
 * Replace placeholders in text with values
 */
export function interpolate(text: string, values: Record<string, string | number>): string {
  return text.replace(/\{(\w+)\}/g, (match, key) => {
    return values[key]?.toString() || match;
  });
}

/**
 * Get pluralized text based on count
 */
export function pluralize(count: number, singular: string, plural?: string): string {
  if (count === 1) {
    return singular;
  }
  return plural || `${singular}s`;
}

/**
 * Format relative time
 */
export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffMinutes < 1) {
    return TEXT.TIME_NOW;
  } else if (diffMinutes === 1) {
    return TEXT.TIME_MINUTE_AGO;
  } else if (diffMinutes < 60) {
    return interpolate(TEXT.TIME_MINUTES_AGO, { minutes: diffMinutes });
  } else if (diffHours === 1) {
    return TEXT.TIME_HOUR_AGO;
  } else if (diffHours < 24) {
    return interpolate(TEXT.TIME_HOURS_AGO, { hours: diffHours });
  } else if (diffDays === 1) {
    return TEXT.TIME_YESTERDAY;
  } else {
    return interpolate(TEXT.TIME_DAYS_AGO, { days: diffDays });
  }
}

// Default export
export default TEXT;