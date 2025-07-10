import { app, BrowserWindow } from 'electron';
import { WindowManager } from '@main/window';
import { TrayManager } from '@main/tray';
import { setupIpcHandlers } from '@main/ipc-handlers';
import { DatabaseService } from '@main/services/DatabaseService';
import { MainConfigService } from '@main/services/ConfigService';
import { HotkeyService } from '@main/services/HotkeyService';

export class AILauncher {
  private isDev = process.env.NODE_ENV === 'development';
  private windowManager: WindowManager;
  private trayManager: TrayManager;
  private hotkeyService!: HotkeyService;
  private databaseService: DatabaseService;
  private configService: MainConfigService;
  private isInitialized = false;

  constructor() {
    this.windowManager = new WindowManager();
    this.trayManager = new TrayManager();
    this.databaseService = new DatabaseService();
    this.configService = MainConfigService.getInstance();
    
    console.log('🔧 AILauncher components created');
    console.log('📍 Environment:', this.isDev ? 'DEVELOPMENT' : 'PRODUCTION');
    console.log('📂 User Data Path:', app.getPath('userData'));
    console.log('📍 App Path:', app.getAppPath());
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) {
      console.log('⚠️ AILauncher already initialized');
      return;
    }
    try {
      console.log('🚀 Initializing AI Launcher...');
      
      if (this.isDev) {
        this.enableDevelopmentFeatures();
      }
      
      console.log('⚙️ Loading configuration...');
      await this.configService.loadConfig();
      
      console.log('📊 Initializing database...');
      await this.databaseService.initialize();
      
      console.log('🪟 Creating main window...');
      await this.windowManager.createMainWindow();

      console.log('⌨️ Initializing Hotkey Service...');
      this.hotkeyService = HotkeyService.getInstance(this.configService, this.windowManager);
      
      console.log('🔌 Setting up IPC handlers...');
      setupIpcHandlers(this.databaseService, this.windowManager, this.hotkeyService);

      await this.windowManager.loadApp();
      
      console.log('📱 Initializing system tray...');
      this.trayManager.initialize();
      
      console.log('⌨️ Registering global shortcuts...');
      this.hotkeyService.registerAll();
      
      console.log('🔗 Binding events...');
      this.bindEvents();
      
      this.isInitialized = true;
      console.log('✅ AI Launcher initialized successfully');
      
      this.showStartupNotification();
      
    } catch (error) {
      console.error('❌ Failed to initialize AI Launcher:', error);
      if (this.isDev) {
        console.error('📋 Error:', error);
        throw error;
      }
    }
  }

  private showStartupNotification(): void {
    this.trayManager.showNotification(
      'AI Launcher',
      'Application started and ready to use!'
    );
  }

  private bindEvents(): void {
    // App events
    app.on('ready', () => console.log('App is ready'));
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') app.quit();
    });
    app.on('activate', async () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        await this.windowManager.createMainWindow();
      }
    });
    app.on('before-quit', () => this.windowManager.setQuitting(true));
    app.on('will-quit', () => this.cleanup());

    this.windowManager.on('window-closed', () => {
        console.log('Window was allowed to close.');
    });
    this.windowManager.on('window-hidden', () => console.log('Window hidden to tray'));

    this.trayManager.on('show-window', () => this.windowManager.showMainWindow());
    this.trayManager.on('hide-window', () => this.windowManager.hideMainWindow());
    this.trayManager.on('toggle-window', () => this.windowManager.toggleMainWindow());
    this.trayManager.on('open-settings', () => this.windowManager.showSettingsWindow());
    this.trayManager.on('quit-app', () => this.quit());
    
  }

  private cleanup(): void {
    try {
      if (this.hotkeyService) {
        this.hotkeyService.unregisterAll();
      }
      
      this.databaseService.cleanup();
      
      console.log('Cleanup completed');
    } catch (error) {
      console.error('Error during cleanup:', error);
    }
  }

  public quit(): void {
    console.log('🔵 Quitting application gracefully...');
    this.windowManager.setQuitting(true);
    app.quit();
  }

  private enableDevelopmentFeatures(): void {
    console.log('🛠️ Enabling development features...');
    
    if (!process.debugPort) {
      console.log('🔍 Main process inspector available at chrome://inspect');
    }
    
    console.log('🌍 Environment Info:', {
      NODE_ENV: process.env.NODE_ENV,
      ELECTRON_IS_DEV: process.env.ELECTRON_IS_DEV,
      userDataPath: app.getPath('userData'),
      version: app.getVersion()
    });
  }

}