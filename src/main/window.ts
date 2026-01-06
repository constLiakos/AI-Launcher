import { app, BrowserWindow, screen, shell, nativeImage } from 'electron';
import { join } from 'path';
import { EventEmitter } from 'events';
import {
  WINDOW_SIZE,
  getWindowSize,
  getCenterPosition,
  getWebPreferences
} from '@shared/constants/index';
import { getAssetsPath, isDev } from '@main/utils/config';
import { MainConfigService } from '@main/services/ConfigService';
import { TIMING } from '@shared/constants/timing.js';
import { WindowState } from '@shared/types';

const SETTINGS_WINDOW_SIZE = {
  WIDTH: 700,
  HEIGHT: 700,
  MIN_WIDTH: 600,
  MIN_HEIGHT: 450,
};

export class WindowManager extends EventEmitter {
  private mainWindow: BrowserWindow | null = null;
  private settingsWindow: BrowserWindow | null = null;
  private isHidden = false;
  private isAppQuitting = false;
  private configService = MainConfigService.getInstance();
  private savePositionDebounce: NodeJS.Timeout | null = null;
  private saveBoundsDebounce: NodeJS.Timeout | null = null;

  constructor() {
    super();
    app.on('before-quit', () => {
      console.log('WindowManager detected app is quitting.');
      this.isAppQuitting = true;
    });
  }

  async createMainWindow(): Promise<BrowserWindow> {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.focus();
      return this.mainWindow;
    }

    const primaryDisplay = screen.getPrimaryDisplay();
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;

    const windowConfig = this.configService.getWindowSettings();

    let width, height, x, y;

    if (windowConfig.rememberedBounds) {
      width = windowConfig.rememberedBounds.width;
      height = windowConfig.rememberedBounds.height;
      x = windowConfig.rememberedBounds.x;
      y = windowConfig.rememberedBounds.y;
    } else {
      const defaultSize = getWindowSize(WindowState.COMPACT, null, null);
      width = defaultSize.width;
      height = defaultSize.height;
      // Use saved position or calculate center position
      const defaultPosition = getCenterPosition(width, height, screenWidth, screenHeight);
      x = windowConfig.position?.x ?? defaultPosition.x;
      y = windowConfig.position?.y ?? defaultPosition.y;
    }

    // 1. Παίρνουμε τα όρια της βασικής οθόνης (Work Area: εξαιρεί taskbars)
    const primaryWorkArea = primaryDisplay.workArea;

    // 2. Υπολογίζουμε το κέντρο του παραθύρου με βάση τις συντεταγμένες που βρήκαμε
    const windowCenterX = x + (width / 2);
    const windowCenterY = y + (height / 2);

    // 3. Ελέγχουμε αν το κέντρο του παραθύρου πέφτει μέσα στη βασική οθόνη
    const isInsidePrimary = (
        windowCenterX >= primaryWorkArea.x &&
        windowCenterX <= (primaryWorkArea.x + primaryWorkArea.width) &&
        windowCenterY >= primaryWorkArea.y &&
        windowCenterY <= (primaryWorkArea.y + primaryWorkArea.height)
    );

    // 4. Αν είναι εκτός, το επαναφέρουμε στο κέντρο της βασικής οθόνης
    if (!isInsidePrimary) {
        console.log('⚠️ Window position detected outside primary screen bounds. Resetting to center.');
        const centerPos = getCenterPosition(width, height, screenWidth, screenHeight);
        
        // Προσθέτουμε το offset της οθόνης (αν η primary δεν ξεκινάει στο 0,0 - σπάνιο αλλά πιθανό σε Linux)
        x = primaryWorkArea.x + centerPos.x;
        y = primaryWorkArea.y + centerPos.y;
    }

    const iconPath = join(getAssetsPath(), 'icons', 'icon.png');
    const icon = nativeImage.createFromPath(iconPath);
    const preloadMainPath = join(__dirname, '../preload/preload.js');

    this.mainWindow = new BrowserWindow({
      width: width,
      height: height,
      minWidth: WINDOW_SIZE.MIN_WIDTH,
      minHeight: WINDOW_SIZE.MIN_HEIGHT,
      x: x,
      y: y,
      show: false,
      frame: false,
      transparent: true,
      alwaysOnTop: windowConfig.alwaysOnTop ?? true,
      skipTaskbar: false,
      resizable: windowConfig.resizable ?? true,
      maximizable: false,
      minimizable: true,
      icon: icon,
      webPreferences: getWebPreferences(isDev, preloadMainPath),
      hasShadow: false,
    });

    // Set window properties
    this.mainWindow.setMenuBarVisibility(false);
    this.mainWindow.setAutoHideMenuBar(true);

    // Bind window events
    this.bindWindowEvents(this.mainWindow, 'main');

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
      this.mainWindow?.focus();
      console.log('Main window is ready to show and focused.');
    });

    return this.mainWindow;
  }
  async loadApp(){
    if (!this.mainWindow) return;

    if (isDev) {
      console.log('Main window loading URL: http://localhost:5173');
      await this.mainWindow.loadURL('http://localhost:5173');
      this.mainWindow.webContents.openDevTools();
    } else {
      const mainHtmlPath = join(__dirname, '../renderer/index.html');
      console.log(`Main window loading file: ${mainHtmlPath}`);
      await this.mainWindow.loadFile(mainHtmlPath);
    }
  }

  async createSettingsWindow(): Promise<BrowserWindow> {
    if (this.settingsWindow && !this.settingsWindow.isDestroyed()) {
      this.settingsWindow.focus();
      console.log('Settings window already exists, focusing.');
      return this.settingsWindow;
    }

    // Find the display where the cursor is currently located (Active Screen)
    const cursorPoint = screen.getCursorScreenPoint();
    const activeDisplay = screen.getDisplayNearestPoint(cursorPoint);
    const { width: screenWidth, height: screenHeight, x: screenX, y: screenY } = activeDisplay.workArea;

    const centerPos = getCenterPosition(
      SETTINGS_WINDOW_SIZE.WIDTH,
      SETTINGS_WINDOW_SIZE.HEIGHT,
      screenWidth,
      screenHeight
    );

    // Add offset to position correctly on the active monitor
    const x = screenX + centerPos.x;
    const y = screenY + centerPos.y;

    const preloadSettingsPath = join(__dirname, '../preload/preload.js');

    this.settingsWindow = new BrowserWindow({
      width: SETTINGS_WINDOW_SIZE.WIDTH,
      height: SETTINGS_WINDOW_SIZE.HEIGHT,
      minWidth: SETTINGS_WINDOW_SIZE.MIN_WIDTH,
      minHeight: SETTINGS_WINDOW_SIZE.MIN_HEIGHT,
      x: x,
      y: y,
      show: false,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      skipTaskbar: false,
      resizable: true,
      maximizable: true,
      minimizable: true,
      modal: false,
      hasShadow: false,
      webPreferences: getWebPreferences(isDev, preloadSettingsPath),
      title: 'AI Launcher Settings',
    });

    this.settingsWindow.setMenuBarVisibility(false);

    const settingsHtmlPath = join(__dirname, '../renderer/settings.html');
    if (isDev) {
      console.log(`Settings window loading URL: http://localhost:5173/settings.html (If configured in Vite) or directly loading file: ${settingsHtmlPath}`);
      try {
        await this.settingsWindow.loadURL('http://localhost:5173/settings.html');
      } catch (e) {
        console.warn('Failed to load settings.html from dev server, trying file path...');
        await this.settingsWindow.loadFile(settingsHtmlPath);
      }
      this.settingsWindow.webContents.openDevTools();
    } else {
      console.log(`Settings window loading file: ${settingsHtmlPath}`);
      await this.settingsWindow.loadFile(settingsHtmlPath);
    }

    this.bindWindowEvents(this.settingsWindow, 'settings');

    this.settingsWindow.once('ready-to-show', () => {
      this.settingsWindow?.show();
      this.settingsWindow?.focus();
      console.log('Settings window is ready to show and focused.');
    });

    this.settingsWindow.on('closed', () => {
      console.log('Settings window closed.');
      this.settingsWindow = null;
    });

    return this.settingsWindow;
  }

  private bindWindowEvents(window: BrowserWindow, windowType: 'main' | 'settings'): void {
    if (!window) return;

    window.on('closed', () => {
      if (windowType === 'main') {
        this.debouncedSaveWindowPosition();
        this.mainWindow = null;
        this.emit('window-closed');
        console.log('Main window event: closed');
      } else {
        console.log('Settings window event: closed');
      }
    });

    if (windowType === 'main') {
      window.on('minimize', () => {
        console.log('Main window event: minimize');
        this.hideMainWindow();
      });

      window.on('close', (event) => {
        if (!this.isAppQuitting) {
          event.preventDefault();
          this.hideMainWindow();
          console.log('Main window event: close intercepted, hiding.');
        } else {
          console.log('Main window event: close allowed (app quitting).');
        }
      });

      window.on('move', async () => {
        this.debouncedSaveWindowPosition();
      });

      window.on('resize', async () => {
        this.debouncedSaveWindowBounds();
      });

      window.on('blur', () => {
        // const alwaysOnTop = this.configService.getWindowSettings().alwaysOnTop;
        // if (!alwaysOnTop && !this.settingsWindow?.isFocused()) {
        //   this.hideMainWindow();
        //   console.log('Main window event: blur, hiding.');
        // }
      });
    }

    window.webContents.setWindowOpenHandler(({ url }) => {
      console.log(`${windowType} window event: opening external link ${url}`);
      shell.openExternal(url);
      return { action: 'deny' };
    });

    window.webContents.on('will-navigate', (event, url) => {
      const allowedHosts = ['localhost:5173'];
      const parsedUrl = new URL(url);
      if (!isDev || (parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'file:')) {
         if (!allowedHosts.includes(parsedUrl.host) && parsedUrl.protocol !== 'file:') {
            console.log(`${windowType} window event: navigation prevented to ${url}`);
            event.preventDefault();
         }
      }
    });
  }

  public showMainWindow(): void {
    if (!this.mainWindow || this.mainWindow.isDestroyed()) {
      console.log('Main window does not exist or is destroyed, creating new one.');
      this.createMainWindow();
      return;
    }

    if (this.mainWindow.isMinimized()) {
      this.mainWindow.restore();
      console.log('Main window restored from minimized state.');
    }

    this.mainWindow.show();
    this.mainWindow.focus();

    this.mainWindow.webContents.send('focus-input');
    this.isHidden = false;
    this.emit('window-shown');
    console.log('Main window shown and focused.');
  }

  public showSettingsWindow(): void {
    if (!this.settingsWindow || this.settingsWindow.isDestroyed()) {
      console.log('Settings window does not exist or is destroyed, creating new one.');
      this.createSettingsWindow();
      return;
    }

    if (this.settingsWindow.isMinimized()) {
      this.settingsWindow.restore();
      console.log('Settings window restored from minimized state.');
    }

    this.settingsWindow.show();
    this.settingsWindow.focus();
    this.isHidden = false;
    this.emit('window-shown');
    console.log('Settings window shown and focused.');
  }

  public hideMainWindow(): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
       if (this.mainWindow.isVisible()) {
         this.saveCurrentPosition();
         this.saveWindowBounds();
       }
      this.mainWindow.hide();
      this.isHidden = true;
      this.emit('window-hidden');
      console.log('Main window hidden.');
    }
  }

  public toggleMainWindow(): void {
    console.log("toggleMainWindow")
    if (!this.mainWindow || this.mainWindow.isDestroyed()) {
      this.createMainWindow();
      return;
    }

    if (this.isHidden || !this.mainWindow.isVisible() || this.mainWindow.isMinimized()) {
      this.showMainWindow();
    } else {
      this.hideMainWindow();
    }
  }

  public resizeMainWindow(width: number|null, height: number|null): void {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      const [currentWidth, currentHeight] = this.mainWindow.getSize();
      if (width === null) width = currentWidth;
      if (height === null) height = currentHeight;

      if (currentWidth !== width || currentHeight !== height) {
        this.mainWindow.setSize(width, height, true);
        console.log(`Main window resized to: ${width}x${height}`);
      }
    }
  }

  public centerWindow(window: BrowserWindow | null): void {
    if (window && !window.isDestroyed()) {
      const primaryDisplay = screen.getPrimaryDisplay();
      const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
      const [windowWidth, windowHeight] = window.getSize();

      const x = Math.round((screenWidth - windowWidth) / 2);
      const y = Math.round((screenHeight - windowHeight) / 2);

      window.setPosition(x, y);
      console.log(`Window centered at: x=${x}, y=${y}`);
    }
  }

  public getMainWindow(): BrowserWindow | null {
    return this.mainWindow;
  }

  public getSettingsWindow(): BrowserWindow | null {
    return this.settingsWindow;
  }

  public isWindowVisible(): boolean {
    return this.mainWindow ? this.mainWindow.isVisible() && !this.mainWindow.isMinimized() : false;
  }

  private isQuitting(): boolean {
    return (global as any).isQuitting === true;
  }

  public setQuitting(quitting: boolean): void {
    (global as any).isQuitting = quitting;
    console.log(`Application quitting state set to: ${quitting}`);
  }

  public destroy(): void {
    console.log('WindowManager destroying all windows...');
    if (this.savePositionDebounce) {
      clearTimeout(this.savePositionDebounce);
      this.savePositionDebounce = null;
    }
    if (this.saveBoundsDebounce) {
      clearTimeout(this.saveBoundsDebounce);
      this.saveBoundsDebounce = null;
    }

    if (this.settingsWindow && !this.settingsWindow.isDestroyed()) {
      this.settingsWindow.close();
      this.settingsWindow = null;
      console.log('Settings window destroyed.');
    }
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
      this.mainWindow.destroy();
      this.mainWindow = null;
      console.log('Main window destroyed.');
    }
  }

  private async saveCurrentPosition() {
    if (!this.mainWindow || this.mainWindow.isDestroyed()) return;
    if (!this.mainWindow.isVisible() || this.mainWindow.isMinimized()) return;

    const [x, y] = this.mainWindow.getPosition();
    try {
      const primaryDisplay = screen.getPrimaryDisplay();
      const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
      if (x < 0 || y < 0 || x > screenWidth || y > screenHeight) {
          console.warn(`Attempted to save off-screen position: x=${x}, y=${y}. Skipping save.`);
          return;
      }

      await this.configService.updateWindowSettings({
        position: { x, y }
      });
      console.log(`Main window position saved: x=${x}, y=${y}`);
    } catch (error) {
      console.error('Failed to save main window position:', error);
    }
  }

  public async saveWindowBounds(): Promise<void> {
    if (this.mainWindow && !this.mainWindow.isDestroyed()) {
       if (!this.mainWindow.isVisible() || this.mainWindow.isMinimized()) return;
      const bounds = this.mainWindow.getBounds();
      await this.configService.updateWindowBounds(bounds);
      console.log(`Main window bounds saved: ${JSON.stringify(bounds)}`);
    }
  }

  private debouncedSaveWindowPosition() {
    if (this.savePositionDebounce) {
      clearTimeout(this.savePositionDebounce);
    }
    this.savePositionDebounce = setTimeout(() => {
      this.saveCurrentPosition();
    }, TIMING.WINDOW_SAVE_DEBOUNCE);
  }

  private debouncedSaveWindowBounds(): void {
    if (this.saveBoundsDebounce) {
      clearTimeout(this.saveBoundsDebounce);
    }

    this.saveBoundsDebounce = setTimeout(async () => {
      await this.saveWindowBounds();
    }, TIMING.WINDOW_SAVE_DEBOUNCE);
  }
}