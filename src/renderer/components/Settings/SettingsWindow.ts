// src/renderer/components/Settings/SettingsWindow.ts
import { APISettingsTab } from '@renderer/components/Settings/ApiSettingsTab';
import { GeneralSettingsTab } from '@renderer/components/Settings/GeneralSettingsTab';
import { HotkeysSettingsTab } from '@renderer/components/Settings/HotkeysSettingsTab';
import { SttSettingsTab } from '@renderer/components/Settings/SttSettingsTab';

import { AppConfig, DEFAULT_CONFIG, mergeWithDefaults, validateConfig } from "@shared/config/AppConfig";
import { HotkeyAction } from '@shared/types';
import { NotificationService } from '@renderer/services/NotificationService';
import { ConfirmationModal } from '@renderer/services/ConfirmationService';


function debounce<F extends (...args: any[]) => any>(func: F, waitFor: number) {
    let timeout: ReturnType<typeof setTimeout> | null = null;

    return (...args: Parameters<F>): void => {
        if (timeout) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(() => func(...args), waitFor);
    };
}


export interface SettingsTab {
  id: string;
  label: string;
  icon: string;
  render: (container: HTMLElement, config: any) => void;
  getFormData?: (container: HTMLElement) => any;
}

export interface SettingsWindowState {
  activeTab: string;
  hasUnsavedChanges: boolean;
  isLoading: boolean;
  appVersion: string;
}

export class SettingsWindow {
  private rootElement: HTMLElement;
  private state: SettingsWindowState;
  private config: any = null;
  private originalConfig: any = null;

  private debouncedDetectChanges: () => void;

  private ConversationSettingsTab = {
    render: (container: HTMLElement, config: any) => { container.innerHTML = '<h3>Conversation Settings</h3><p>Content for conversation settings...</p>'; }
  };
  private AdvancedSettingsTab = {
    render: (container: HTMLElement, config: any) => { container.innerHTML = '<h3>Advanced Settings</h3><p>Content for advanced settings...</p>'; }
  };


  private tabs: SettingsTab[] = [
    {
      id: 'general',
      label: 'General',
      icon: '⚙️',
      render: GeneralSettingsTab.render,
      getFormData: GeneralSettingsTab.getFormData
    },
    {
      id: 'api',
      label: 'API Settings',
      icon: '🔗',
      render: APISettingsTab.render.bind(APISettingsTab),
      getFormData: APISettingsTab.getFormData.bind(APISettingsTab)
    },
    { 
      id: 'stt',
      label: 'STT',
      icon: '🎙️',
      render: SttSettingsTab.render.bind(SttSettingsTab),
      getFormData: SttSettingsTab.getFormData.bind(SttSettingsTab)
    },
    { 
      id: 'hotkeys', 
      label: 'Hotkeys', 
      icon: '⌨️', 
      render: HotkeysSettingsTab.render,
      getFormData: HotkeysSettingsTab.getFormData
    },
    { id: 'conversation', label: 'Conversation', icon: '💬', render: this.ConversationSettingsTab.render },
    { id: 'advanced', label: 'Advanced', icon: '🔧', render: this.AdvancedSettingsTab.render }
  ];

  constructor(rootElement: HTMLElement) {
    this.rootElement = rootElement;
    this.state = {
      activeTab: 'general',
      hasUnsavedChanges: false,
      isLoading: false,
      appVersion: 'loading...'
    };
    this.debouncedDetectChanges = debounce(this.detectChanges.bind(this), 300);
  }

  // =============================================================================
  // INITIALIZATION
  // =============================================================================
  public async initialize(): Promise<void> {
    try {
      this.renderBaseLayout();
      await this.loadAppVersion();
      await this.loadConfiguration();
      this.bindSettingsEvents();
      console.log('SettingsWindow initialized in its own window.');
    } catch (error) {
      console.error('Failed to initialize SettingsWindow:', error);
      this.rootElement.innerHTML = `<p style="color: red; padding: 20px;">Error initializing settings: ${error instanceof Error ? error.message : error}</p>`;
    }
  }

  private renderBaseLayout(): void {
    if (!this.rootElement) {
      console.error('Root element for SettingsWindow is not defined.');
      return;
    }
    this.rootElement.classList.add('settings-window');
    this.rootElement.innerHTML = this.getSettingsHTML();
  }

  private async loadAppVersion(): Promise<void> {
    try {
      if (window.electronAPI && typeof window.electronAPI.getAppVersion === 'function') {
        const version = await window.electronAPI.getAppVersion();
        this.state.appVersion = version || 'N/A';
        const versionElement = this.rootElement.querySelector('.settings-version');
        if (versionElement) {
          versionElement.textContent = `v${this.state.appVersion}`;
        }
      } else {
          this.state.appVersion = 'N/A (API Error)';
          console.warn('window.electronAPI.getAppVersion is not available.')
      }
    } catch (error) {
      console.error('Failed to load app version:', error);
      this.state.appVersion = 'Error';
    }
  }

  private getSettingsHTML(): string {
    return `
            <div class="settings-header">
              <div class="settings-title">
                <h2>⚙️ Settings</h2>
                <div class="settings-version">v${this.state.appVersion}</div>
              </div>
            </div>
            <div class="settings-body">
              <nav class="settings-tabs">
                ${this.tabs.map(tab => `
                  <button
                    class="settings-tab ${tab.id === this.state.activeTab ? 'active' : ''}"
                    data-tab="${tab.id}"
                  >
                    <span class="tab-icon">${tab.icon}</span>
                    <span class="tab-label">${tab.label}</span>
                  </button>
                `).join('')}
              </nav>
              <div class="settings-content">
                 <div class="settings-loading ${this.state.isLoading ? 'visible' : ''}">
                    <div class="loading-spinner"></div>
                 </div>
                 <div id="settings-tab-content-area"></div>
              </div>
            </div>
            <div class="settings-footer">
              <div class="settings-actions-left">
              <button class="btn btn-secondary" data-action="reset" title="Reset all settings to their default values">
                🔄 Reset Defaults
              </button>
              <button class="btn btn-secondary" data-action="export" title="Export current settings to a JSON file">
                📤 Export Config
              </button>
              <button class="btn btn-secondary" data-action="import" title="Import settings from a JSON file">
                📥 Import Config
              </button>
              </div>
              <div class="settings-actions-right">
                <button class="btn btn-secondary" data-action="cancel">Cancel</button>
                <button class="btn btn-primary" data-action="save" disabled>
                  💾 Save Changes
                </button>
              </div>
            </div>
            <div id="notification-container" class="notification-container"></div>
          `;
  }

  // =============================================================================
  // TAB MANAGEMENT
  // =============================================================================

  public switchTab(tabId: string, forceRender: boolean = false): void {
      if (!forceRender && this.state.activeTab === tabId) return;
      const selectedTab = this.tabs.find(tab => tab.id === tabId);
      if (!selectedTab) {
        console.warn(`Invalid tab ID: ${tabId}`);
        return;
      }
      this.state.activeTab = tabId;
      this.updateTabNavigation();
      const contentArea = this.rootElement.querySelector<HTMLElement>('#settings-tab-content-area');
      if (contentArea) {
        contentArea.innerHTML = '';
        try {
          if (selectedTab.id === 'hotkeys') {
              (selectedTab.render as any)(contentArea, this.handleSettingsChange.bind(this));
          } else {
              (selectedTab.render as any)(contentArea, this.config);
          }
        } catch (e) {
          contentArea.innerHTML = `<p style="color:red; padding:10px;">Error rendering tab: ${tabId}</p>`;
          console.error(`Error rendering tab ${tabId}:`, e);
        }
      }
  }

  private updateTabNavigation(): void {
    const tabsElements = this.rootElement.querySelectorAll<HTMLButtonElement>('.settings-tab');
    tabsElements.forEach(tabEl => {
      if (tabEl.getAttribute('data-tab') === this.state.activeTab) {
        tabEl.classList.add('active');
      } else {
        tabEl.classList.remove('active');
      }
    });
  }


  // =============================================================================
  // CONFIGURATION MANAGEMENT
  // =============================================================================
  private async loadConfiguration(): Promise<void> {
    if (!window.electronAPI?.loadConfig) {
      NotificationService.showError('Configuration API is not available.');
      return;
    }
    try {
      this.setLoading(true);
      const loadedConfig = await window.electronAPI.loadConfig();
      if (loadedConfig) {
        this.config = loadedConfig;
        this.originalConfig = JSON.parse(JSON.stringify(loadedConfig));
        console.log('Configuration loaded:', this.config);
      } else {
        NotificationService.showError('Failed to load configuration. Using defaults.');
        this.config = { ...DEFAULT_CONFIG };
        this.originalConfig = { ...DEFAULT_CONFIG };
      }
    } catch (error) {
      NotificationService.showError(`Failed to load settings: ${error instanceof Error ? error.message : String(error)}`);
      this.config = { ...DEFAULT_CONFIG };
      this.originalConfig = { ...DEFAULT_CONFIG };
    } finally {
      this.setLoading(false);
      this.switchTab(this.state.activeTab, true);
    }
  }

  private async saveConfiguration(): Promise<void> {
    if (!this.state.hasUnsavedChanges) {
      console.log('No changes to save.');
      return;
    }

    if (!window.electronAPI?.saveConfig || !window.electronAPI?.saveHotkeySettings) {
      NotificationService.showError('Cannot save settings. API not available.');
      return;
    }

    this.setLoading(true);

    try {
      const savePromises: Promise<any>[] = [];

      // Detecting changes in Hotkeys
      const hotkeysChanged = JSON.stringify(this.config.hotkeys) !== JSON.stringify(this.originalConfig.hotkeys);

      if (hotkeysChanged) {
        console.log('Saving hotkey settings...');
        savePromises.push(window.electronAPI.saveHotkeySettings(this.config.hotkeys));
      }

      // Detecting changes in other settings
      const currentOtherSettings = { ...this.config };
      delete (currentOtherSettings as any).hotkeys;

      const originalOtherSettings = { ...this.originalConfig };
      delete (originalOtherSettings as any).hotkeys;

      const otherSettingsChanged = JSON.stringify(currentOtherSettings) !== JSON.stringify(originalOtherSettings);

      if (otherSettingsChanged || hotkeysChanged) {
         console.log('Saving general configuration...');
         savePromises.push(window.electronAPI.saveConfig(this.config));
      }
      
      if (savePromises.length > 0) {
        await Promise.all(savePromises);
        
        this.originalConfig = JSON.parse(JSON.stringify(this.config));
        this.state.hasUnsavedChanges = false;
        
        NotificationService.showSuccess('Settings saved successfully!');
        console.log('Configuration saved:', this.config);
      } else {
        this.state.hasUnsavedChanges = false; 
      }

    } catch (error) {
      NotificationService.showError(`Failed to save settings: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      this.setLoading(false);
      this.updateSaveButtonState();
    }
  }


  // =============================================================================
  // EVENT HANDLING
  // =============================================================================

  private bindSettingsEvents(): void {
    if (!this.rootElement) return;

    this.rootElement.querySelectorAll<HTMLButtonElement>('.settings-tab').forEach(tabButton => {
      tabButton.addEventListener('click', (e) => {
        const tabId = (e.currentTarget as HTMLElement).getAttribute('data-tab');
        if (tabId) this.switchTab(tabId);
      });
    });

    this.rootElement.querySelectorAll<HTMLButtonElement>('[data-action]').forEach(button => {
      button.addEventListener('click', (e) => {
        const action = (e.currentTarget as HTMLElement).getAttribute('data-action');
        this.handleAction(action);
      });
    });

    const contentArea = this.rootElement.querySelector('.settings-content');
    if (contentArea) {
      contentArea.addEventListener('input', this.debouncedDetectChanges);
      contentArea.addEventListener('change', this.debouncedDetectChanges);
    }
  }

  private handleAction(action: string | null): void {
    switch (action) {
      case 'cancel':
        window.close();
        break;
      case 'save':
        this.saveConfiguration();
        break;
      case 'reset':
        this.resetToDefaults();
        break;
      case 'export':
        this.exportConfiguration();
        break;
      case 'import':
        this.importConfiguration();
        break;
      default:
        console.warn(`Unknown action: ${action}`);
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  
  private handleSettingsChange(): void {
    this.debouncedDetectChanges();
  }
  
  private setLoading(loading: boolean): void {
    this.state.isLoading = loading;
    const loadingEl = this.rootElement.querySelector<HTMLElement>('.settings-loading');
    if (loadingEl) {
      loadingEl.style.display = loading ? 'flex' : 'none';
    }
    this.updateSaveButtonState();
  }

  private detectChanges(): void {
    const activeTabDef = this.tabs.find(t => t.id === this.state.activeTab);
    const contentArea = this.rootElement.querySelector<HTMLElement>('#settings-tab-content-area');

    if (activeTabDef?.getFormData && contentArea) {
      const formData = activeTabDef.getFormData(contentArea);

      for (const key in formData) {
        const formKey = key as keyof AppConfig;

        if (formKey === 'hotkeys' && typeof formData.hotkeys === 'object' && formData.hotkeys !== null) {
          for (const actionKey in formData.hotkeys) {
            const action = actionKey as HotkeyAction;
            
            if (this.config.hotkeys[action] && formData.hotkeys[action]) {
              this.config.hotkeys[action] = {
                ...this.config.hotkeys[action],
                ...formData.hotkeys[action],
              };
            }
          }
        } else if (typeof formData[formKey] === 'object' && !Array.isArray(formData[formKey]) && this.config[formKey]) {
          this.config[formKey] = { ...this.config[formKey], ...formData[formKey] } as any;
        } else {
          (this.config as any)[formKey] = formData[formKey];
        }
      }

      const hasChanges = JSON.stringify(this.config) !== JSON.stringify(this.originalConfig);

      if (hasChanges !== this.state.hasUnsavedChanges) {
        this.state.hasUnsavedChanges = hasChanges;
        this.updateSaveButtonState();
      }
    }
  }

  private updateSaveButtonState(): void {
    const saveBtn = this.rootElement.querySelector<HTMLButtonElement>('[data-action="save"]');
    if (saveBtn) {
      saveBtn.disabled = !this.state.hasUnsavedChanges || this.state.isLoading;
      if (this.state.isLoading) {
        saveBtn.innerHTML = `💾 Saving...`;
      } else {
        saveBtn.innerHTML = this.state.hasUnsavedChanges ? `💾 Save Changes` : `✅ Saved`;
      }
    }
  }

  private collectFormData(): any {
    const activeTabDef = this.tabs.find(t => t.id === this.state.activeTab);
    const contentArea = this.rootElement.querySelector<HTMLElement>('#settings-tab-content-area');

    if (activeTabDef && activeTabDef.getFormData && contentArea) {
      const activeTabData = activeTabDef.getFormData(contentArea);
      return {
        ...this.config,
        [this.state.activeTab]: {
          ...this.config[this.state.activeTab],
          ...activeTabData,
        }
      };
    }

    console.warn(`Tab ${this.state.activeTab} does not have a getFormData method.`);
    return { ...this.config };
  }


  private populateSettingsFields(): void {
    console.log('Populating settings fields. Active tab should re-render or update.');
    this.switchTab(this.state.activeTab, true);
  }

  private async resetToDefaults(): Promise<void> {
    if (!window.electronAPI || !window.electronAPI.resetConfig || !window.electronAPI.loadConfig) {
      NotificationService.showError('Configuration API is not available for reset.');
      return;
    }

    try {
      await ConfirmationModal.show({
        title: 'Reset to Default Settings',
        message: 'Are you sure you want to reset all settings to their default values? This action cannot be undone.',
        confirmText: 'Yes, Reset',
      });

      this.setLoading(true);
      await window.electronAPI.resetConfig();
      await this.loadConfiguration();

      this.state.hasUnsavedChanges = false;
      this.updateSaveButtonState();
      NotificationService.showSuccess('Settings have been reset to defaults.');

    } catch (error) {
      if (error) {
        NotificationService.showError(`Failed to reset settings: ${error instanceof Error ? error.message : String(error)}`);
      } else {
        console.log('Reset to defaults was cancelled by the user.');
      }
    } finally {
      this.setLoading(false);
    }
  }

  private async exportConfiguration(): Promise<void> {
    if (!window.electronAPI?.saveFile) {
      NotificationService.showError('Export API is not available.');
      return;
    }
    try {
      const configJson = JSON.stringify(this.config, null, 2);
      const defaultPath = `ai-launcher-settings-${new Date().toISOString().split('T')[0]}.json`;

      const filePath = await window.electronAPI.saveFile({
        title: 'Export Settings',
        defaultPath: defaultPath,
        content: configJson,
        filters: [{ name: 'JSON Files', extensions: ['json'] }]
      });

      if (filePath) {
        NotificationService.showSuccess(`Settings successfully exported to ${filePath}`);
      } else {
        console.log('Export cancelled by user.');
      }
    } catch (error) {
      NotificationService.showError(`Failed to export settings: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async importConfiguration(): Promise<void> {
    if (!window.electronAPI?.openFile) {
      NotificationService.showError('Import API is not available.');
      return;
    }

    try {
      const result = await window.electronAPI.openFile({ /* ... options ... */ });
      if (!result || !result.content) {
        console.log('File selection was cancelled.');
        return;
      }

      await ConfirmationModal.show({
        title: 'Confirm Settings Import',
        message: `Are you sure you want to import settings from "${result.filePath}"? This will overwrite your current unsaved changes.`,
        confirmText: 'Import & Overwrite',
      });
      
      this.setLoading(true);

      let parsedConfig;
      try {
        parsedConfig = JSON.parse(result.content);
      } catch (e) {
        NotificationService.showError('Invalid JSON file. Could not parse the settings file.');
        this.setLoading(false);
        return;
      }

      if (validateConfig(parsedConfig)) {
        this.config = mergeWithDefaults(parsedConfig);
        await this.saveConfiguration();
        await this.loadConfiguration();
        NotificationService.showSuccess('Settings imported and saved successfully.');
      } else {
        NotificationService.showError('Invalid configuration file. The file is not compatible.');
      }

    } catch (error) {
      if (error) {
         NotificationService.showError(`Import failed: ${error instanceof Error ? error.message : String(error)}`);
      } else {
         console.log('Import was cancelled by the user.');
      }
    } finally {
      this.setLoading(false);
    }
  }

  public destroy(): void {
    if (this.rootElement) {
      this.rootElement.innerHTML = '';
    }
    console.log('SettingsWindow UI destroyed.');
  }
}