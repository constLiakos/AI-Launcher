import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { app } from 'electron';
import { AppConfig, DEFAULT_CONFIG, mergeWithDefaults } from '@shared/config/AppConfig';
import { LLMProvider, Settings, WindowStateData } from '@shared/types';
import { v4 as uuidv4 } from 'uuid';

export class MainConfigService {
  private static instance: MainConfigService;
  private config: AppConfig;
  private configPath: string;
  private windowState: WindowStateData;
  private windowStatePath: string;


  private constructor() {
    this.config = { ...DEFAULT_CONFIG };
    this.windowState = {
      position: null,
      rememberedBounds: null,
    };
    this.configPath = this.getConfigPath('config.json');
    this.windowStatePath = this.getConfigPath('window-state.json');
  }

  static getInstance(): MainConfigService {
    if (!MainConfigService.instance) {
      MainConfigService.instance = new MainConfigService();
    }
    return MainConfigService.instance;
  }
  async loadWindowState(): Promise<void> {
    try {
      if (existsSync(this.windowStatePath)) {
        const stateData = await readFile(this.windowStatePath, 'utf-8');
        const savedState = JSON.parse(stateData);
        this.windowState = {
          ...this.windowState,
          ...savedState
        };
        console.log('Window state loaded successfully');
      } else {
        console.log('No window state file found, using defaults');
        await this.saveWindowState();
      }
    } catch (error) {
      console.error('Failed to load window state:', error);
      this.windowState = { position: null, rememberedBounds: null };
    }
  }

  async saveWindowState(): Promise<void> {
    try {
      const stateDir = dirname(this.windowStatePath);
      if (!existsSync(stateDir)) {
        await mkdir(stateDir, { recursive: true });
      }
      await writeFile(this.windowStatePath, JSON.stringify(this.windowState, null, 2));
      console.log('Window state saved successfully');
    } catch (error) {
      console.error('Failed to save window state:', error);
    }
  }
  // =============================================================================
  // CONFIGURATION MANAGEMENT
  // =============================================================================

  async loadConfig(): Promise<void> {
    await this.loadWindowState(); 
    
    try {
      if (existsSync(this.configPath)) {
        const configData = await readFile(this.configPath, 'utf-8');
        const savedConfig = JSON.parse(configData);
        this.config = mergeWithDefaults(savedConfig);
        console.log('Config loaded and merged successfully');
      } else {
        console.log('No config file found, using defaults');
        this.config = { ...DEFAULT_CONFIG };
        await this.saveConfig();
      }
    } catch (error) {
      console.error('Failed to load config:', error);
      this.config = { ...DEFAULT_CONFIG };
    }
  }
  async saveConfig(): Promise<void> {
    try {
      const configDir = dirname(this.configPath);
      if (!existsSync(configDir)) {
        await mkdir(configDir, { recursive: true });
      }

      await writeFile(this.configPath, JSON.stringify(this.config, null, 2));
      console.log('Config saved successfully');
    } catch (error) {
      console.error('Failed to save config:', error);
      throw error;
    }
  }

  async saveSettings(settings: Settings): Promise<void> {
    console.log('ConfigService: saving settings');
    this.config = { ...this.config, ...settings };
    await this.saveConfig();
  }

  // =============================================================================
  // GETTERS
  // =============================================================================

  getConfig(): AppConfig {
    return { ...this.config };
  }

  getTheme(): string {
    return this.config.theme;
  }

  getApiSettings(): LLMProvider | null {
    const defaultProviderId = this.config.defaultProviderId;
    if (!defaultProviderId) {
      return null;
    }
    const provider = this.config.providers.find(p => p.id === defaultProviderId);
    return provider || null;
  }

  getLLMProviders(): LLMProvider[] {
    return [...this.config.providers];
  }

  getDefaultLLMProviderId(): string | null {
    return this.config.defaultProviderId;
  }

  getWindowSettings() {
    return { 
      ...this.config.window,
      ...this.windowState 
    };
  }

  getHotkeySettings() {
    return { ...this.config.hotkeys };
  }

  // =============================================================================
  // SETTERS
  // =============================================================================


  async updateConfig(updates: Partial<AppConfig>): Promise<void> {
    this.config = { ...this.config, ...updates };
    await this.saveConfig();
  }

  async updateTheme(theme: string): Promise<void> {
    this.config.theme = theme as any;
    await this.saveConfig();
  }

  async setDefaultLLMProvider(id: string): Promise<void> {
    // Checking if the provider exists in the list
    if (this.config.providers.some(p => p.id === id)) {
      this.config.defaultProviderId = id;
      await this.saveConfig();
    } else {
      throw new Error(`Provider with ID ${id} not found.`);
    }
  }

  async addLLMProvider(providerData: Omit<LLMProvider, 'id'>): Promise<LLMProvider> {
    const newProvider: LLMProvider = {
      ...providerData,
      id: uuidv4(),
    };

    this.config.providers.push(newProvider);
    
    if (this.config.providers.length === 1) {
        this.config.defaultProviderId = newProvider.id;
    }

    await this.saveConfig();
    return newProvider;
  }
  async updateLLMProvider(providerToUpdate: LLMProvider): Promise<void> {
    const index = this.config.providers.findIndex(p => p.id === providerToUpdate.id);
    if (index > -1) {
      this.config.providers[index] = providerToUpdate;
      await this.saveConfig();
    } else {
      throw new Error(`Provider with ID ${providerToUpdate.id} not found for update.`);
    }
  }

  async deleteLLMProvider(id: string): Promise<void> {
    const providers = this.config.providers;
    
    if (providers.length <= 1) {
        throw new Error("Cannot delete the last provider.");
    }
    
    const initialLength = providers.length;
    this.config.providers = providers.filter(p => p.id !== id);

    if (this.config.providers.length === initialLength) {
        throw new Error(`Provider with ID ${id} not found for deletion.`);
    }
    if (this.config.defaultProviderId === id) {
      this.config.defaultProviderId = this.config.providers.length > 0 ? this.config.providers[0].id : null;
    }
    await this.saveConfig();
  }

  async updateWindowSettings(settings: Partial<WindowStateData>): Promise<void> {
    this.windowState = { ...this.windowState, ...settings };
    await this.saveWindowState();
  }


  async updateWindowBounds(bounds: { x: number; y: number; width: number; height: number }): Promise<void> {
    this.windowState = {
      ...this.windowState,
      rememberedBounds: bounds,
      position: { x: bounds.x, y: bounds.y }
    };
    await this.saveWindowState();
    
    // Update the dimensions in the main config (if needed)
    this.config.window.dimensions = {
      ...this.config.window.dimensions,
      width: bounds.width,
      height: bounds.height
    };
    await this.saveConfig();
  }

  // =============================================================================
  // UTILITIES
  // =============================================================================

  public getConfigPath(filename: string): string {
    return join(app.getPath('userData'), filename);
  }

  resetToDefaults(): void {
    this.config = { ...DEFAULT_CONFIG };
    this.saveConfig();
  }

  exportConfig(): string {
    return JSON.stringify(this.config, null, 2);
  }

  async importConfig(configJson: string): Promise<boolean> {
    try {
      const importedConfig = JSON.parse(configJson);
      // Basic validation
      if (typeof importedConfig === 'object' && importedConfig !== null) {
        this.config = { ...DEFAULT_CONFIG, ...importedConfig };
        await this.saveConfig();
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }

  public async updateConfigSection<K extends keyof AppConfig>(
    section: K,
    updates: AppConfig[K] extends object 
      ? Partial<AppConfig[K]> 
      : AppConfig[K]
  ): Promise<void> {
    const currentValue = this.config[section];
    
    if (currentValue && typeof currentValue === 'object' && !Array.isArray(currentValue)) {
      // Object type - merge with spread
      this.config[section] = { 
        ...currentValue, 
        ...(updates as Partial<AppConfig[K]>) 
      } as AppConfig[K];
    } else {
      // Primitive type - direct assignment
      this.config[section] = updates as AppConfig[K];
    }
    
    await this.saveConfig();
  }

}

