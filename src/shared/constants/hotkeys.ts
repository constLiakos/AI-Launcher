// =============================================================================
// HOTKEY DEFINITIONS
// =============================================================================

export const GLOBAL_HOTKEYS = {
  // Main application hotkeys
  TOGGLE_WINDOW: 'Alt+X',
  HIDE_WINDOW: 'Escape',
  QUIT_APP: 'Ctrl+Q',
  
  // Speech-to-Text hotkeys
  TOGGLE_RECORDING: 'Ctrl+Shift+R',
  START_RECORDING: 'F2',
  STOP_RECORDING: 'F3',
  
  // UI hotkeys
  OPEN_SETTINGS: 'Ctrl+S',
  TOGGLE_INPUT_MODE: 'Tab',
  TOGGLE_CONVERSATION: 'F4',
  FOCUS_INPUT: 'Ctrl+L',
  
  // Message actions
  SEND_MESSAGE: 'Enter',
  NEW_LINE: 'Shift+Enter',
  CLEAR_INPUT: 'Ctrl+K',
  
  // Navigation
  PREVIOUS_CONVERSATION: 'Ctrl+Up',
  NEXT_CONVERSATION: 'Ctrl+Down',
  NEW_CONVERSATION: 'Ctrl+N',
  
  // Development
  TOGGLE_DEVTOOLS: 'F12',
  RELOAD_APP: 'Ctrl+R'
} as const;

// =============================================================================
// HOTKEY CATEGORIES
// =============================================================================

export const HOTKEY_CATEGORIES = {
  GLOBAL: {
    name: 'Global Shortcuts',
    description: 'System-wide keyboard shortcuts',
    hotkeys: {
      TOGGLE_WINDOW: GLOBAL_HOTKEYS.TOGGLE_WINDOW,
      TOGGLE_RECORDING: GLOBAL_HOTKEYS.TOGGLE_RECORDING
    }
  },
  
  WINDOW: {
    name: 'Window Management',
    description: 'Window and application control',
    hotkeys: {
      HIDE_WINDOW: GLOBAL_HOTKEYS.HIDE_WINDOW,
      QUIT_APP: GLOBAL_HOTKEYS.QUIT_APP,
      OPEN_SETTINGS: GLOBAL_HOTKEYS.OPEN_SETTINGS
    }
  },
  
  INPUT: {
    name: 'Input & Messaging',
    description: 'Text input and message handling',
    hotkeys: {
      SEND_MESSAGE: GLOBAL_HOTKEYS.SEND_MESSAGE,
      NEW_LINE: GLOBAL_HOTKEYS.NEW_LINE,
      CLEAR_INPUT: GLOBAL_HOTKEYS.CLEAR_INPUT,
      TOGGLE_INPUT_MODE: GLOBAL_HOTKEYS.TOGGLE_INPUT_MODE
    }
  },
  
  RECORDING: {
    name: 'Voice Recording',
    description: 'Speech-to-text controls',
    hotkeys: {
      START_RECORDING: GLOBAL_HOTKEYS.START_RECORDING,
      STOP_RECORDING: GLOBAL_HOTKEYS.STOP_RECORDING
    }
  },
  
  CONVERSATION: {
    name: 'Conversation Management',
    description: 'Navigate and manage conversations',
    hotkeys: {
      TOGGLE_CONVERSATION: GLOBAL_HOTKEYS.TOGGLE_CONVERSATION,
      NEW_CONVERSATION: GLOBAL_HOTKEYS.NEW_CONVERSATION,
      PREVIOUS_CONVERSATION: GLOBAL_HOTKEYS.PREVIOUS_CONVERSATION,
      NEXT_CONVERSATION: GLOBAL_HOTKEYS.NEXT_CONVERSATION
    }
  },
  
  DEVELOPMENT: {
    name: 'Development Tools',
    description: 'Developer shortcuts (only in dev mode)',
    hotkeys: {
      TOGGLE_DEVTOOLS: GLOBAL_HOTKEYS.TOGGLE_DEVTOOLS,
      RELOAD_APP: GLOBAL_HOTKEYS.RELOAD_APP
    }
  }
} as const;

// =============================================================================
// PLATFORM-SPECIFIC HOTKEYS
// =============================================================================

export const PLATFORM_HOTKEYS = {
  win32: {
    TOGGLE_WINDOW: 'Alt+X',
    QUIT_APP: 'Ctrl+Q',
    OPEN_SETTINGS: 'Ctrl+Comma',
    SELECT_ALL: 'Ctrl+A',
    COPY: 'Ctrl+C',
    PASTE: 'Ctrl+V',
    CUT: 'Ctrl+X',
    UNDO: 'Ctrl+Z',
    REDO: 'Ctrl+Y'
  },
  
  darwin: {
    TOGGLE_WINDOW: 'Cmd+Space',
    QUIT_APP: 'Cmd+Q',
    OPEN_SETTINGS: 'Cmd+Comma',
    SELECT_ALL: 'Cmd+A',
    COPY: 'Cmd+C',
    PASTE: 'Cmd+V',
    CUT: 'Cmd+X',
    UNDO: 'Cmd+Z',
    REDO: 'Cmd+Shift+Z'
  },
  
  linux: {
    TOGGLE_WINDOW: 'Alt+X',
    QUIT_APP: 'Ctrl+Q',
    OPEN_SETTINGS: 'Ctrl+Comma',
    SELECT_ALL: 'Ctrl+A',
    COPY: 'Ctrl+C',
    PASTE: 'Ctrl+V',
    CUT: 'Ctrl+X',
    UNDO: 'Ctrl+Z',
    REDO: 'Ctrl+Y'
  }
} as const;

// =============================================================================
// HOTKEY VALIDATION & UTILITIES
// =============================================================================

/**
 * Valid modifier keys for hotkeys
 */
export const MODIFIERS = {
  CTRL: 'Ctrl',
  ALT: 'Alt',
  SHIFT: 'Shift',
  CMD: 'Cmd',       // macOS only
  CMDORCTRL: 'CmdOrCtrl', // Cross-platform Ctrl/Cmd
  SUPER: 'Super'    // Linux Super key
} as const;

/**
 * Valid key codes for hotkeys
 */
export const KEY_CODES = {
  // Function keys
  F1: 'F1', F2: 'F2', F3: 'F3', F4: 'F4', F5: 'F5', F6: 'F6',
  F7: 'F7', F8: 'F8', F9: 'F9', F10: 'F10', F11: 'F11', F12: 'F12',
  
  // Arrow keys
  UP: 'Up', DOWN: 'Down', LEFT: 'Left', RIGHT: 'Right',
  
  // Special keys
  ENTER: 'Return', SPACE: 'Space', TAB: 'Tab', ESCAPE: 'Escape',
  BACKSPACE: 'Backspace', DELETE: 'Delete',
  
  // Letters (A-Z)
  A: 'A', B: 'B', C: 'C', D: 'D', E: 'E', F: 'F', G: 'G', H: 'H',
  I: 'I', J: 'J', K: 'K', L: 'L', M: 'M', N: 'N', O: 'O', P: 'P',
  Q: 'Q', R: 'R', S: 'S', T: 'T', U: 'U', V: 'V', W: 'W', X: 'X',
  Y: 'Y', Z: 'Z',
  
  // Numbers
  NUM_0: '0', NUM_1: '1', NUM_2: '2', NUM_3: '3', NUM_4: '4',
  NUM_5: '5', NUM_6: '6', NUM_7: '7', NUM_8: '8', NUM_9: '9'
} as const;

/**
 * Get platform-specific hotkey
 */
export function getPlatformHotkey(hotkeyName: keyof typeof PLATFORM_HOTKEYS.win32): string {
  const platform = process.platform as keyof typeof PLATFORM_HOTKEYS;
  const platformHotkeys = PLATFORM_HOTKEYS[platform] || PLATFORM_HOTKEYS.win32;
  return platformHotkeys[hotkeyName] || GLOBAL_HOTKEYS.TOGGLE_WINDOW;
}

/**
 * Parse hotkey string into components
 */
export function parseHotkey(hotkey: string): {
  modifiers: string[];
  key: string;
  isValid: boolean;
} {
  const parts = hotkey.split('+').map(part => part.trim());
  const key = parts.pop() || '';
  const modifiers = parts;
  
  // Validate modifiers
  const validModifiers = Object.values(MODIFIERS);
  const invalidModifiers = modifiers.filter(mod => !validModifiers.includes(mod as any));
  
  // Validate key
  const validKeys = Object.values(KEY_CODES);
  const isValidKey = validKeys.includes(key as any) || /^[a-zA-Z0-9]$/.test(key);
  
  return {
    modifiers,
    key,
    isValid: invalidModifiers.length === 0 && isValidKey && key.length > 0
  };
}

/**
 * Format hotkey for display
 */
export function formatHotkeyForDisplay(hotkey: string): string {
  const { modifiers, key } = parseHotkey(hotkey);
  
  // Platform-specific formatting
  if (process.platform === 'darwin') {
    const macModifiers = modifiers.map(mod => {
      switch (mod) {
        case 'Ctrl': return '⌃';
        case 'Cmd': return '⌘';
        case 'Alt': return '⌥';
        case 'Shift': return '⇧';
        case 'CmdOrCtrl': return '⌘';
        default: return mod;
      }
    });
    return `${macModifiers.join('')}${key}`;
  }
  
  // Windows/Linux formatting
  return `${modifiers.join('+')}${modifiers.length > 0 ? '+' : ''}${key}`;
}

/**
 * Check if hotkey is global (system-wide)
 */
const GLOBAL_HOTKEY_LIST = [
  GLOBAL_HOTKEYS.TOGGLE_WINDOW,
  GLOBAL_HOTKEYS.TOGGLE_RECORDING
] as const;

// export function isGlobalHotkey(hotkey: string): boolean {
//   const globalHotkeys = [
//     GLOBAL_HOTKEYS.TOGGLE_WINDOW,
//     GLOBAL_HOTKEYS.TOGGLE_RECORDING
//   ];
//   return globalHotkeys.includes(hotkey);
// }

/**
 * Check if hotkey is global (system-wide)
 */
export function isGlobalHotkey(hotkey: string): boolean {
  return (GLOBAL_HOTKEY_LIST as readonly string[]).includes(hotkey);
}

/**
 * Get default hotkeys configuration
 */
export function getDefaultHotkeys(): Record<string, string> {
  return {
    // Global shortcuts
    toggleWindow: GLOBAL_HOTKEYS.TOGGLE_WINDOW,
    toggleRecording: GLOBAL_HOTKEYS.TOGGLE_RECORDING,
    
    // Window management
    hideWindow: GLOBAL_HOTKEYS.HIDE_WINDOW,
    quitApp: GLOBAL_HOTKEYS.QUIT_APP,
    openSettings: GLOBAL_HOTKEYS.OPEN_SETTINGS,
    
    // Input shortcuts
    sendMessage: GLOBAL_HOTKEYS.SEND_MESSAGE,
    newLine: GLOBAL_HOTKEYS.NEW_LINE,
    clearInput: GLOBAL_HOTKEYS.CLEAR_INPUT,
    toggleInputMode: GLOBAL_HOTKEYS.TOGGLE_INPUT_MODE,
    
    // Conversation shortcuts
    toggleConversation: GLOBAL_HOTKEYS.TOGGLE_CONVERSATION,
    newConversation: GLOBAL_HOTKEYS.NEW_CONVERSATION,
    previousConversation: GLOBAL_HOTKEYS.PREVIOUS_CONVERSATION,
    nextConversation: GLOBAL_HOTKEYS.NEXT_CONVERSATION,
    
    // Development shortcuts
    toggleDevtools: GLOBAL_HOTKEYS.TOGGLE_DEVTOOLS,
    reloadApp: GLOBAL_HOTKEYS.RELOAD_APP
  };
}

/**
 * Validate hotkey conflicts
 */
export function validateHotkeyConflicts(hotkeys: Record<string, string>): {
  isValid: boolean;
  conflicts: Array<{ keys: string[]; hotkey: string }>;
} {
  const conflicts: Array<{ keys: string[]; hotkey: string }> = [];
  const hotkeyMap = new Map<string, string[]>();
  
  // Group hotkeys by their key combination
  Object.entries(hotkeys).forEach(([key, hotkey]) => {
    if (!hotkeyMap.has(hotkey)) {
      hotkeyMap.set(hotkey, []);
    }
    hotkeyMap.get(hotkey)!.push(key);
  });
  
  // Find conflicts (same hotkey assigned to multiple actions)
  hotkeyMap.forEach((keys, hotkey) => {
    if (keys.length > 1) {
      conflicts.push({ keys, hotkey });
    }
  });
  
  return {
    isValid: conflicts.length === 0,
    conflicts
  };
}

// =============================================================================
// HOTKEY DESCRIPTIONS
// =============================================================================

export const HOTKEY_DESCRIPTIONS: Record<string, string> = {
  [GLOBAL_HOTKEYS.TOGGLE_WINDOW]: 'Show/hide the main window',
  [GLOBAL_HOTKEYS.HIDE_WINDOW]: 'Hide the window to system tray',
  [GLOBAL_HOTKEYS.QUIT_APP]: 'Quit the application',
  [GLOBAL_HOTKEYS.TOGGLE_RECORDING]: 'Start/stop voice recording',
  [GLOBAL_HOTKEYS.START_RECORDING]: 'Start voice recording',
  [GLOBAL_HOTKEYS.STOP_RECORDING]: 'Stop voice recording',
  [GLOBAL_HOTKEYS.OPEN_SETTINGS]: 'Open application settings',
  [GLOBAL_HOTKEYS.TOGGLE_INPUT_MODE]: 'Switch between single-line and multi-line input',
  [GLOBAL_HOTKEYS.TOGGLE_CONVERSATION]: 'Show/hide conversation history',
  [GLOBAL_HOTKEYS.FOCUS_INPUT]: 'Focus the input field',
  [GLOBAL_HOTKEYS.SEND_MESSAGE]: 'Send the current message',
  [GLOBAL_HOTKEYS.NEW_LINE]: 'Add a new line (in multi-line mode)',
  [GLOBAL_HOTKEYS.CLEAR_INPUT]: 'Clear the input field',
  [GLOBAL_HOTKEYS.PREVIOUS_CONVERSATION]: 'Go to previous conversation',
  [GLOBAL_HOTKEYS.NEXT_CONVERSATION]: 'Go to next conversation',
  [GLOBAL_HOTKEYS.NEW_CONVERSATION]: 'Start a new conversation',
  [GLOBAL_HOTKEYS.TOGGLE_DEVTOOLS]: 'Toggle developer tools',
  [GLOBAL_HOTKEYS.RELOAD_APP]: 'Reload the application'
};

// =============================================================================
// EXPORT TYPES
// =============================================================================

export type HotkeyName = keyof typeof GLOBAL_HOTKEYS;
export type HotkeyCategory = keyof typeof HOTKEY_CATEGORIES;
export type ModifierKey = keyof typeof MODIFIERS;
export type KeyCode = keyof typeof KEY_CODES;

// Default export
export default GLOBAL_HOTKEYS;