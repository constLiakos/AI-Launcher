// src/renderer/settingsRenderer.ts
import '@renderer/styles/main.css';
import '@renderer/styles/components/confirmation-modal.css';
import '@renderer/styles/components/settings-window.css';
import '@renderer/styles/components/hotkeys-settings-tab.css';
import '@renderer/styles/components/api-settings-tab.css';
import { ConfirmationModal } from '@renderer/services/ConfirmationService';

import '@fortawesome/fontawesome-free/css/all.min.css';

import { SettingsWindow } from '@renderer/components/Settings/SettingsWindow';
import ThemeManager from '@renderer/managers/ThemeManager';
import { ThemeType } from '@shared/constants/themes'; // <-- NEW: Import ThemeType
import { AppConfig } from '@shared/config/AppConfig';
import { NotificationService } from '@renderer/services/NotificationService'; 

console.log('Settings Renderer Loaded!');

class SettingsApp {
  private themeManager: ThemeManager = ThemeManager.getInstance();

  constructor() {
    ConfirmationModal.init();

    this.listenForConfigChanges();
    this.initializeTheme();
    this.initializeApp();
  }

  private initializeApp(): void {
    const rootElement = document.getElementById('settings-root');
    if (!rootElement) {
      console.error('Settings root element not found!');
      return;
    }
  
    // The existing logic for SettingsWindow can remain
    const settingsManager = new SettingsWindow(rootElement);
    settingsManager.initialize();

    const notificationContainer = document.getElementById('notification-container');
    if (notificationContainer) {
        NotificationService.init(notificationContainer);
    }
  }

  // --- NEW: Theme initialization logic ---
  private initializeTheme(): void {    
    this.loadThemePreference();
    
    // Optional: Listen for theme changes if settings can change it live
    this.themeManager.addListener((theme: ThemeType) => {
      this.applyTheme(theme);
    });
    
    // Apply initial theme
    this.applyTheme(this.themeManager.getCurrentThemeType());
  }

  private async loadThemePreference(): Promise<void> {
    try {
      if (window.electronAPI) {
        const config = await window.electronAPI.loadConfig();
        if (config?.theme) {
          this.themeManager.setTheme(config.theme);
        } else {
          // Fallback to a default theme if not set
          this.themeManager.setTheme(ThemeType.CLASSIC); 
        }
      }
    } catch (error) {
      const error_msg = 'Failed to load user preferences for theme, using default'
      console.warn(error_msg, error);
      this.themeManager.setTheme(ThemeType.CLASSIC); // Fallback in case of error
      NotificationService.showError(error_msg);
    }
  }

  private listenForConfigChanges(): void {
    if (window.electronAPI?.onConfigUpdate) {
      window.electronAPI.onConfigUpdate((newConfig: Partial<AppConfig>) => {
        console.log('Received config update from main process:', newConfig);
        console.log(this.themeManager.getCurrentThemeType())

        if (newConfig.theme && newConfig.theme !== this.themeManager.getCurrentThemeType()) {
          console.log(`Theme changed to ${newConfig.theme}. Updating...`);
          // this.themeManager.setTheme(newConfig.theme);
          this.applyTheme(newConfig.theme)
        }
      });
    } else {
      console.warn('`onThemeUpdate` is not available on electronAPI.');
    }
  }

  private applyTheme(themeType: ThemeType): void {
    this.themeManager.setTheme(themeType);
    // Remove any existing theme class
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    // Add the new theme class
    document.body.classList.add(`theme-${themeType.toLowerCase()}`);
    
    const themeColors = this.themeManager.getTheme(themeType);
    const root = document.documentElement;
    // Apply CSS variables
    Object.entries(themeColors).forEach(([key, value]) => {
      const cssVar = `--${key.replace(/_/g, '-')}`;
      root.style.setProperty(cssVar, value as string);
    });
  }
}

// Ensure the DOM is ready before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new SettingsApp());
} else {
    new SettingsApp();
}