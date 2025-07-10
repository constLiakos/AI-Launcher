import { ConversationSettings, HotkeyAction, HotkeySettings, LLMProvider, LLMProviderType, Preferences, STTProviderType, STTSettings, WindowDimensions, WindowSettings } from '../types';
import { ThemeType } from '@shared/constants/themes';
import { v4 as uuidv4 } from 'uuid';

// =============================================================================
// INTERFACES
// =============================================================================


// =============================================================================
// DEFAULT CONFIGURATION
// =============================================================================

export interface AppConfig {
  theme: ThemeType;
  preferences: Preferences;
  window: WindowSettings;
  providers: LLMProvider[];
  defaultProviderId: string | null;
  defaultChatModelId: string | null; 
  stt: STTSettings;
  conversation: ConversationSettings;
  hotkeys: HotkeySettings;
}

const defaultOpenAIProvider: LLMProvider = {
  id: uuidv4(),
  name: 'OpenAI Default',
  type: LLMProviderType.OPENAI,
  apiKey: '',
  apiBase: 'https://api.openai.com/v1',
  timeout: 120000,
  temperature: 0.7,
  maxTokens: 2000,
  systemPrompt: "You're a friendly assistant delivering clear, concise answers for everyday learning and fun facts. Keep replies brief, use tables for clarity, and make learning quick and enjoyable.",
  availableModels: [],
  customModels: []
};


export const DEFAULT_CONFIG: AppConfig = {
  theme: ThemeType.CLASSIC,
  preferences: {
    autostart: false,
    showDockIcon: true,
    confirmOnQuit: true,
    confirmOnDelete: true,
  },
  window: {
    dimensions: { width: 650, height: 130, minWidth: 400, minHeight: 130 },
    alwaysOnTop: true,
    startMinimized: false,
    frame: false,
    transparent: false,
    resizable: true,
  },
  providers: [defaultOpenAIProvider],
  defaultProviderId: defaultOpenAIProvider.id,
  defaultChatModelId: null,
  stt: {
    enabled: true,
    provider: STTProviderType.OPENAI,
    apiBase: 'https://api.openai.com/v1',
    apiKey: '',
    model: 'whisper-1',
    timeout: 15000,
  },
  conversation: {
      historyLimit: 100,
      clearHistoryOnMinimize: false,
      clearLastResponseOnMinimize: false,
      pdfProcessingStrategy: 'extractText'
  },
  hotkeys: {
    [HotkeyAction.ToggleWindow]: {
      action: HotkeyAction.ToggleWindow,
      accelerator: 'CommandOrControl+Shift+A',
      label: 'Toggle App Window',
      isEditable: true,
    },
    [HotkeyAction.OpenSettings]: {
      action: HotkeyAction.OpenSettings,
      accelerator: 'CommandOrControl+,',
      label: 'Open Settings',
      isEditable: true,
    },
    [HotkeyAction.StartRecording]: {
      action: HotkeyAction.StartRecording,
      accelerator: 'CommandOrControl+Shift+R',
      label: 'Start Voice Recording',
      isEditable: true,
    },
  },
};

// =============================================================================
// UTILITY FUNCTIONS (no window dependencies)
// =============================================================================

/**
 * Validate configuration object
 */
export function validateConfig(config: Partial<AppConfig>): boolean {
  try {
    // Validate theme
    if (config.theme && !Object.values(ThemeType).includes(config.theme)) {
      return false;
    }
    // Validate window dimensions
    if (config.window?.dimensions) {
      const { width, height, minWidth, minHeight } = config.window.dimensions;
      if (width < minWidth || height < minHeight) {
        return false;
      }
    }
    
    // Validate providers
    if (config.providers) {
      if (!Array.isArray(config.providers)) return false;
      for (const provider of config.providers) {
        if (!provider.id || !provider.name || !provider.type) {
          return false;
        }
      }
      if (config.defaultProviderId && !config.providers.some(p => p.id === config.defaultProviderId)) {
        return false; // defaultProviderId must exist in the providers list
      }
    }
    
    return true;
  } catch {
    return false;
  }
}

/**
 * Merge config with defaults
 */
export function mergeWithDefaults(config: Partial<AppConfig>): AppConfig {
  // Deep merge for nested objects is important
  return {
    ...DEFAULT_CONFIG,
    ...config,
    preferences: { ...DEFAULT_CONFIG.preferences, ...config.preferences },
    window: { ...DEFAULT_CONFIG.window, ...config.window },
    stt: { ...DEFAULT_CONFIG.stt, ...config.stt },
    conversation: { ...DEFAULT_CONFIG.conversation, ...config.conversation },
    hotkeys: { ...DEFAULT_CONFIG.hotkeys, ...config.hotkeys },
    // Custom logic for providers to avoid duplicates and ensure defaults
    providers: config.providers && config.providers.length > 0 ? config.providers : DEFAULT_CONFIG.providers,
    defaultProviderId: config.defaultProviderId !== undefined ? config.defaultProviderId : DEFAULT_CONFIG.defaultProviderId,
  };
}

/**
 * Export configuration to JSON string
 */
export function exportConfigToJSON(config: AppConfig): string {
  return JSON.stringify(config, null, 2);
}

/**
 * Import configuration from JSON string
 */
export function importConfigFromJSON(jsonString: string): AppConfig | null {
  try {
    const parsed = JSON.parse(jsonString);
    if (validateConfig(parsed)) {
      return mergeWithDefaults(parsed);
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Get configuration difference between two configs
 */
export function getConfigDiff(
  oldConfig: AppConfig, 
  newConfig: AppConfig
): Partial<AppConfig> {
  const diff: any = {};
  
  Object.keys(newConfig).forEach(key => {
    const oldValue = (oldConfig as any)[key];
    const newValue = (newConfig as any)[key];
    
    if (JSON.stringify(oldValue) !== JSON.stringify(newValue)) {
      diff[key] = newValue;
    }
  });
  
  return diff;
}

// =============================================================================
// TYPE GUARDS
// =============================================================================

/**
 * Check if object is valid AppConfig
 */
export function isValidAppConfig(obj: any): obj is AppConfig {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    typeof obj.theme === 'string' &&
    typeof obj.window === 'object' &&
    Array.isArray(obj.providers) &&
    (typeof obj.defaultProviderId === 'string' || obj.defaultProviderId === null) &&
    typeof obj.stt === 'object' &&
    typeof obj.conversation === 'object' &&
    typeof obj.hotkeys === 'object' &&
    typeof obj.preferences === 'object'
  );
}

// =============================================================================
// HELPER FUNCTIONS FOR SPECIFIC SETTINGS
// =============================================================================
export function createLLMProvider(overrides: Partial<LLMProvider>): LLMProvider {
    const id = overrides.id || uuidv4();
    return {
        ...defaultOpenAIProvider, // Start with a base default
        ...overrides,
        id: id, // Ensure id is always present
    };
}
/**
 * Create minimal API settings
 */
// export function createApiSettings(overrides: Partial<ApiSettings> = {}): ApiSettings {
//   return {
//     ...DEFAULT_CONFIG.api,
//     ...overrides
//   };
// }

/**
 * Create minimal window settings
 */
export function createWindowSettings(overrides: Partial<WindowSettings> = {}): WindowSettings {
  return {
    ...DEFAULT_CONFIG.window,
    ...overrides
  };
}

/**
 * Create minimal hotkey settings
 */
export function createHotkeySettings(overrides: Partial<HotkeySettings> = {}): HotkeySettings {
  return {
    ...DEFAULT_CONFIG.hotkeys,
    ...overrides
  };
}
