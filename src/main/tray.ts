import { Tray, Menu, nativeImage, app } from 'electron';
import { join } from 'path';
import { EventEmitter } from 'events';
import { TEXT } from '@shared/constants/index';
import { getAssetsPath } from '@main/utils/config';

export class TrayManager extends EventEmitter {
  private tray: Tray | null = null;
  private isInitialized = false;

  public initialize(): void {
    if (this.isInitialized) return;

    try {
      const iconPath = this.getTrayIconPath();
      const icon = nativeImage.createFromPath(iconPath);
      
      const trayIcon = icon.resize({ width: 16, height: 16 });
      
      this.tray = new Tray(trayIcon);
      
      this.tray.setToolTip(TEXT.TRAY_TOOLTIP);
      this.tray.setIgnoreDoubleClickEvents(false);
      
      this.updateTrayMenu();
      this.bindTrayEvents();
      
      this.isInitialized = true;
      console.log('System tray initialized');
    } catch (error) {
      console.error('Failed to initialize system tray:', error);
    }
  }

  private getTrayIconPath(): string {
      const assetsPath = getAssetsPath();
      const iconsPath = join(assetsPath, 'icons');

      if (process.platform === 'win32') {
        return join(iconsPath, 'tray-icon.ico');
      } else if (process.platform === 'darwin') {
        return join(iconsPath, 'tray-iconTemplate.png');
      } else {
        return join(iconsPath, 'tray-icon.png');
      }
  }

  private bindTrayEvents(): void {
    if (!this.tray) return;

    // Single click to toggle window
    this.tray.on('click', () => {
      this.emit('toggle-window');
    });

    // Double click to show window
    this.tray.on('double-click', () => {
      this.emit('show-window');
    });

    // Right click to show context menu
    this.tray.on('right-click', () => {
      if (this.tray) {
        this.tray.popUpContextMenu();
      }
    });
  }

  private updateTrayMenu(): void {
    if (!this.tray) return;

    const contextMenu = Menu.buildFromTemplate([
      {
        label: TEXT.TRAY_SHOW,
        click: () => {
          this.emit('show-window');
        }
      },
      {
        label: TEXT.TRAY_HIDE,
        click: () => {
          this.emit('hide-window');
        }
      },
      { type: 'separator' },
      {
        label: TEXT.TRAY_SETTINGS,
        click: () => {
          this.emit('open-settings');
        }
      },
      { type: 'separator' },
      {
        label: TEXT.TRAY_QUIT,
        click: () => {
          this.emit('quit-app');
        }
      }
    ]);

    this.tray.setContextMenu(contextMenu);
  }

  public showNotification(title: string, body: string): void {
    if (this.tray) {
      this.tray.displayBalloon({
        title,
        content: body,
        icon: nativeImage.createFromPath(this.getTrayIconPath())
      });
    }
  }

    public setTrayIcon(iconPath: string): void {
    if (this.tray) {
        const icon = nativeImage.createFromPath(iconPath);
        // this.tray.setIcon(icon.resize({ width: 16, height: 16 }));
        this.tray.setImage(icon.resize({ width: 16, height: 16 }));
    }
    }

  public updateTrayTitle(title: string): void {
    if (this.tray) {
      this.tray.setTitle(title);
    }
  }

  public destroy(): void {
    if (this.tray) {
      this.tray.destroy();
      this.tray = null;
      this.isInitialized = false;
    }
  }
}

