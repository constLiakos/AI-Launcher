// src/renderer/renderer.ts
import '@renderer/styles/main.css';
import '@renderer/styles/components/confirmation-modal.css';
import '@renderer/styles/components/conversation-area.css'; // Keep styles
import '@renderer/styles/components/chat-window.css';
import 'highlight.js/styles/github-dark.css';
import { ConfirmationModal } from '@renderer/services/ConfirmationService';


import { ThemeType } from '@shared/constants/themes';
import ThemeManager from './managers/ThemeManager';
import { ChatWindow } from './components/ChatWindow'; // Import ChatWindow
import { AppConfig } from '@shared/config/AppConfig';
import { NotificationService } from './services/NotificationService'; 

class AILauncherRenderer {
  private themeManager: ThemeManager = ThemeManager.getInstance();
  private chatWindow: ChatWindow;

  constructor() {
    
    this.listenForConfigChanges();
    this.initializeTheme();
    this.initializeChatWindow();
    this.setupGlobalShortcuts();
    this.setupFocusListener();

    const notificationContainer = document.getElementById('notification-container');
    if (notificationContainer) {
        NotificationService.init(notificationContainer);
    }
    ConfirmationModal.init();

    console.log('🚀 AI Launcher Renderer initialized');
  }

  private setupFocusListener(): void {
    if (window.electronAPI?.onFocusInput) {
      window.electronAPI.onFocusInput(() => {
        console.log('Received focus-input event from main process.');
        this.chatWindow?.focusInput(); // <-- Κλήση μεθόδου στο ChatWindow
      });
    } else {
      console.warn('`onFocusInput` is not available on electronAPI.');
    }
  }

  private initializeChatWindow(): void {
    const appContainer = document.getElementById('app') as HTMLElement;
    if (!appContainer) {
        console.error('Fatal: #app container not found!');
        return;
    }
    this.chatWindow = new ChatWindow(appContainer);
  }

  private initializeTheme(): void {    
    // Logic for loading user preferences for theme
    this.loadThemePreference();
    
    // Listen for theme changes from the manager
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
          this.themeManager.setTheme(ThemeType.CLASSIC); // Default
        }
      }
    } catch (error) {
      const error_msg = 'Failed to load user preferences, using default theme:'
      console.warn(error_msg, error);
      this.themeManager.setTheme(ThemeType.CLASSIC);
      NotificationService.showError(error_msg);
    }
  }

  private applyTheme(themeType: ThemeType): void {
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${themeType.toLowerCase()}`);
    
    const themeColors = this.themeManager.getTheme(themeType);
    const root = document.documentElement;
    Object.entries(themeColors).forEach(([key, value]) => {
      const cssVar = `--${key.replace(/_/g, '-')}`;
      root.style.setProperty(cssVar, value as string);
    });
  }
  
  private setupGlobalShortcuts(): void {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.hideWindow();
      }
    });
  }

  private listenForConfigChanges(): void {
    if (window.electronAPI?.onConfigUpdate) {
      window.electronAPI.onConfigUpdate((newConfig: Partial<AppConfig>) => {
        console.log('Received config update from main process:', newConfig);

        if (newConfig.theme && newConfig.theme !== this.themeManager.getCurrentThemeType()) {
          console.log(`Theme changed to ${newConfig.theme}. Updating...`);
          this.themeManager.setTheme(newConfig.theme);
        }
      });
    } else {
      console.warn('`onThemeUpdate` is not available on electronAPI.');
    }
  }

  private hideWindow(): void {
    if (window.electronAPI) {
      window.electronAPI.hideWindow();
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new AILauncherRenderer();
});