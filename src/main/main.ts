import { app, BrowserWindow, shell} from 'electron';
import { AILauncher } from '@main/AILauncher';

// Initialize the application
const aiLauncher = new AILauncher();

// Handle app ready event
app.whenReady().then(() => {
  aiLauncher.initialize();
});

// Handle second instance (single instance lock)
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    // Someone tried to run a second instance, focus our window instead
    const mainWindow = BrowserWindow.getAllWindows().find(win => win.webContents.getURL().includes('index.html'));
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}
  
// Security: Control window creation and navigation
app.on('web-contents-created', (_, contents) => {
  // Modern way to handle window opening (replaces deprecated 'new-window')
  contents.setWindowOpenHandler(({ url }) => {
    console.log(`Window open requested: ${url}`);
    
    // Allow opening external URLs in default browser
    if (url.startsWith('https://') || url.startsWith('http://')) {
      shell.openExternal(url).catch(err => {
        console.error('Failed to open external URL:', err);
      });
    }
    
    // Always deny creating new electron windows
    return { action: 'deny' };
  });

  // Prevent navigation away from our app
  contents.on('will-navigate', (event, navigationUrl) => {
    try {
      const parsedUrl = new URL(navigationUrl);
      
      // Allow navigation patterns based on environment
      const allowedPatterns = process.env.NODE_ENV === 'development' 
        ? ['localhost', '127.0.0.1', 'file:']
        : ['file:'];
      
      const isAllowed = allowedPatterns.some(pattern => 
        navigationUrl.includes(pattern) || parsedUrl.protocol === 'file:'
      );
      
      if (!isAllowed) {
        console.log(`Blocked navigation to: ${navigationUrl}`);
        event.preventDefault();
      }
    } catch (error) {
      console.error('Error parsing navigation URL:', error);
      event.preventDefault();
    }
  });

  // Additional security headers and CSP
  contents.on('did-finish-load', () => {
    if (process.env.NODE_ENV === 'development') {
      // In development, allow some flexibility
      contents.executeJavaScript(`
        if (!window.process) {
          console.log('Security: Node integration properly disabled');
        }
      `);
    }
  });
});

// Handle certificate errors in development
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (process.env.NODE_ENV === 'development') {
    // In development, ignore certificate errors for localhost
    if (url.startsWith('https://localhost') || url.startsWith('https://127.0.0.1')) {
      event.preventDefault();
      callback(true);
      return;
    }
  }
  
  // In production, always validate certificates
  callback(false);
});

// Disable experimental features that could pose security risks
app.commandLine.appendSwitch('disable-features', 'OutOfBlinkCors');

export default aiLauncher;