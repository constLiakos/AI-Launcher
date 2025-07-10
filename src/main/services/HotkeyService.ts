// src/main/services/HotkeyService.ts

import { globalShortcut } from 'electron';
import { HotkeyAction, HotkeyConfig, HotkeySettings } from '@shared/types';
import { MainConfigService } from '@main/services/ConfigService';
import { WindowManager } from '@main/window';

// Define the default hotkey configuration
export const DEFAULT_HOTKEYS: HotkeySettings = {
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
      isEditable: true
  }
};

export class HotkeyService {
  private static instance: HotkeyService;
  private configService: MainConfigService;
  private windowManager: WindowManager;
  private currentHotkeys: HotkeySettings;

  private constructor(configService: MainConfigService, windowManager: WindowManager) {
    this.configService = configService;
    this.windowManager = windowManager;
    this.currentHotkeys = this.loadHotkeys();
  }

  public static getInstance(configService: MainConfigService, windowManager: WindowManager): HotkeyService {
    if (!HotkeyService.instance) {
      HotkeyService.instance = new HotkeyService(configService, windowManager);
    }
    return HotkeyService.instance;
  }

  private loadHotkeys(): HotkeySettings {
    const config = this.configService.getConfig();
    // Merge saved hotkeys with defaults to ensure all actions are covered
    return {
      ...DEFAULT_HOTKEYS,
      ...(config.hotkeys || {}),
    };
  }

  public getSettings(): HotkeySettings {
    return this.currentHotkeys;
  }

  public async saveAndReloadHotkeys(newSettings: Partial<HotkeySettings>): Promise<void> {
    const currentConfig = this.configService.getConfig();
    
    // Merge the partial new settings with the existing hotkey settings
    const updatedHotkeys: HotkeySettings = { ...this.currentHotkeys };
    for (const key in newSettings) {
        const action = key as HotkeyAction;
        if(updatedHotkeys[action] && updatedHotkeys[action].isEditable) {
            updatedHotkeys[action].accelerator = newSettings[action]?.accelerator || null;
        }
    }

    // Update the main config object
    await this.configService.updateConfig({ ...currentConfig, hotkeys: updatedHotkeys });
    
    // Reload hotkeys from the source of truth (config) and re-register
    this.currentHotkeys = this.loadHotkeys();
    this.registerAll();
  }

  public registerAll(): void {
    globalShortcut.unregisterAll();
    console.log('Registering hotkeys...');
    for (const hotkey of Object.values(this.currentHotkeys)) {
      if (hotkey.accelerator) {
        try {
            globalShortcut.register(hotkey.accelerator, () => {
                this.executeAction(hotkey.action);
            });
            console.log(`Registered: ${hotkey.label} -> ${hotkey.accelerator}`);
        } catch (error) {
            console.error(`Failed to register hotkey "${hotkey.accelerator}" for ${hotkey.label}:`, error);
        }
      }
    }
  }

  public unregisterAll(): void {
    globalShortcut.unregisterAll();
  }

  private executeAction(action: HotkeyAction): void {
    console.log(`Executing hotkey action: ${action}`);
    switch (action) {
      case HotkeyAction.ToggleWindow:
        this.windowManager.toggleMainWindow();
        break;
      case HotkeyAction.OpenSettings:
        this.windowManager.showSettingsWindow();
        break;
      case HotkeyAction.StartRecording:
        this.windowManager.getMainWindow()?.webContents.send('hotkey:start-recording');
        break;
      // Add other cases as needed
    }
  }
}