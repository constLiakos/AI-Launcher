import * as fs from 'fs';
import { ipcMain, dialog, shell, app, BrowserWindow, desktopCapturer, screen } from 'electron';
import { DatabaseService } from '@main/services/DatabaseService';
import { ConversationService } from '@main/services/ConversationService';
import { MessageService } from '@main/services/MessageService';
import { MainConfigService } from '@main/services/ConfigService';
import { MessageCreate, stringToMessageRole } from '@shared/database-types';
import { writeFile, readFile } from 'fs/promises';
import { AppConfig } from '@shared/config/AppConfig';
import { WindowManager } from '@main/window';
import { Settings, HotkeySettings, LLMProvider, IPCResponse, AIMessage, Model, MessageRole, Attachment, PdfProcessResponse } from '@shared/types';
import { HotkeyService } from '@main/services/HotkeyService';
import { AIService } from '@main/services/AIService';
import { AttachmentService } from '@main/services/AttachmentService';
import { SttService } from '@main/services/SttService';


export function setupIpcHandlers(
  databaseService: DatabaseService, 
  windowManager: WindowManager,
  hotkeyService: HotkeyService
): void {
  const conversationService = new ConversationService(databaseService);
  const messageService = new MessageService(databaseService, conversationService);
  const configService = MainConfigService.getInstance();
  const attachmentService = AttachmentService.getInstance(configService.getConfig());
  const sttService = new SttService();

  const aiService = new AIService();
  // =============================================================================
  // CONFIGURATION MANAGEMENT
  // =============================================================================

  ipcMain.handle('config:load', async () => {
    try {
      return configService.getConfig();
    } catch (error) {
      console.error('Failed to load config via IPC:', error);
      return null;
    }
  });

  ipcMain.handle('config:save', async (event, config: Partial<AppConfig>) => {
    try {
      await configService.updateConfig(config);

      BrowserWindow.getAllWindows().forEach(window => {
        window.webContents.send('config-updated', config);
      });

      return true;
    } catch (error) {
      console.error('Failed to save config via IPC:', error);
      throw error;
    }
  });

  ipcMain.handle('config:reset', async (event) => {
    try {
      await configService.resetToDefaults()
    } catch (error) {
      console.error('Failed to save config via IPC:', error);
      throw error;
    }
  });

  ipcMain.handle('config:export', async (event) => {
    try {
      return await configService.exportConfig();
    } catch (error) {
      console.error('Failed to save config via IPC:', error);
      throw error;
    }
  });
  ipcMain.handle('get-screen-sources', async (event) => {
    const sources = await desktopCapturer.getSources({ 
        types: ['window', 'screen'],
        fetchWindowIcons: true,
        thumbnailSize: { width: 300, height: 300 } 
    });
    return sources.map(source => ({
      id: source.id,
      name: source.name,
      thumbnail: source.thumbnail.toDataURL(),
      appIcon: source.appIcon ? source.appIcon.toDataURL() : null
    }));
  });

  ipcMain.handle('capture-high-res-source', async (event, sourceId: string) => {
    if (!sourceId) {
      throw new Error('Source ID is required');
    }

    const primaryDisplay = screen.getPrimaryDisplay();
    const requiredSize = primaryDisplay.size;

    const sources = await desktopCapturer.getSources({
      types: ['window', 'screen'],
      thumbnailSize: {
        width: requiredSize.width,
        height: requiredSize.height
      }
    });

    const selectedSource = sources.find(s => s.id === sourceId);

    if (!selectedSource) {
      throw new Error(`Source with ID "${sourceId}" not found or has been closed.`);
    }

    return selectedSource.thumbnail.toDataURL();
  });

  ipcMain.handle('stt:transcribe', async (_event, audioData: Uint8Array) => {
    try {
      const audioBuffer = Buffer.from(audioData);
      
      const transcription = await sttService.transcribe(audioBuffer);
      return transcription;
    } catch (error) {
      console.error('IPC Handler Error [stt:transcribe]:', error);
      throw error; 
    }
  });

  ipcMain.handle(
    'download-attachment',
    async (event, args: { dataUrl: string; filename: string }) => {
      try {
        const { dataUrl, filename } = args;

        if (!dataUrl || !filename) {
          throw new Error('Invalid arguments: dataUrl and filename are required.');
        }

        const window = BrowserWindow.fromWebContents(event.sender);
        if (!window) {
          throw new Error('Could not find the associated browser window.');
        }

        const result = await dialog.showSaveDialog(window, {
          title: 'Save Attachment',
          defaultPath: filename,
          buttonLabel: 'Save',
        });

        if (result.canceled || !result.filePath) {
          console.log('Attachment download cancelled by user.');
          return { success: true, cancelled: true };
        }
        const base64Data = dataUrl.split(';base64,').pop();
        if (!base64Data) {
          throw new Error('Invalid Data URL format.');
        }
        
        const buffer = Buffer.from(base64Data, 'base64');

        fs.writeFileSync(result.filePath, buffer);

        console.log(`Attachment saved successfully to: ${result.filePath}`);
        
        return { success: true, path: result.filePath };

      } catch (error) {
        console.error('Failed to download attachment:', error);
        return { success: false, error: (error as Error).message };
      }
    }
  );

  ipcMain.handle('process-pdf-attachment', async (event, dataUrl: string): Promise<PdfProcessResponse> => {
    try {
      const result = await attachmentService.processPdf(dataUrl);
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  });

  ipcMain.handle('config:get-path', () => {
    return configService.getConfigPath('config.json');
  });

  ipcMain.handle('config:import', async (event, configJson: string) => {
    try {
      return await configService.importConfig(configJson);
    } catch (error) {
      console.error('Failed to import config:', error);
      return false;
    }
  });

  // =============================================================================
  // AI SERVICE OPERATIONS
  // =============================================================================
  ipcMain.handle('ai:generate-response', async (event, messages: AIMessage[]) => {
    try {
      const response = await aiService.generateResponse(messages);
      return response;
    } catch (error) {
      console.error('Failed to generate AI response:', error);
      throw error;
    }
  });
  ipcMain.handle('ai:generate-stream', async (event, payload: { messages: AIMessage[], tempMessageId: string, modelId: string, providerId: string }) => {
    aiService.generateResponseStream(payload, event.sender);
  });

  ipcMain.handle('ai:fetch-models', async (event, provider: LLMProvider): Promise<IPCResponse<Model[]>> => {
    try {
      const models = await aiService.fetchAvailableModels(provider);
      return { success: true, data: models };
    } catch (error) {
      console.error('Failed to fetch AI models via IPC:', error);
      return { success: false, error: (error as Error).message, data: [] };
    }
  });

  // =============================================================================
  // WINDOW MANAGEMENT
  // =============================================================================

  ipcMain.handle('window:resize', async (event, width: number|null, height: number|null) => {
    windowManager.resizeMainWindow(width, height)
  });

  ipcMain.handle('window:hide', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window) {
      window.hide();
    }
  });

  ipcMain.handle('window:show', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window) {
      window.show();
      window.focus();
    }
  });

  ipcMain.handle('window:minimize', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window) {
      window.minimize();
    }
  });

  ipcMain.handle('window:close', async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window) {
      window.close();
    }
  });

  ipcMain.handle('window:set-always-on-top', async (event, flag: boolean) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window) {
      window.setAlwaysOnTop(flag);
    }
  });

  ipcMain.handle('attachment:download', async (event, dataUrl: string) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (!window) return false;

    try {
      // Extract mime type and base64 data
      const matches = dataUrl.match(/^data:(.+);base64,(.+)$/);
      if (!matches || matches.length !== 3) {
        throw new Error('Invalid data URL format.');
      }
      
      const mimeType = matches[1];
      const base64Data = matches[2];
      const extension = mimeType.split('/')[1] || 'png';
      
      const { canceled, filePath } = await dialog.showSaveDialog(window, {
        title: 'Save Attachment',
        defaultPath: `attachment-${Date.now()}.${extension}`,
        filters: [{ name: 'Images', extensions: [extension, 'jpg', 'png', 'gif'] }]
      });

      if (!canceled && filePath) {
        const buffer = Buffer.from(base64Data, 'base64');
        await fs.promises.writeFile(filePath, buffer);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to download attachment:', error);
      dialog.showErrorBox('Download Error', 'Could not save the attachment. Please try again.');
      return false;
    }
  });


  ipcMain.handle('settings:open', async (event, flag: boolean) => {
    await windowManager.showSettingsWindow();
  });

  ipcMain.handle('settings:save', async (event, settings: Settings) => {
    try {
      await configService.saveSettings(settings);
      return { success: true };
    } catch (error) {
      console.error('Failed to save settings via IPC:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // =============================================================================
  // DATABASE OPERATIONS - CONVERSATIONS
  // =============================================================================

  ipcMain.handle('db:conversations:create', async (event, title: string) => {
    try {
      const conversation = await conversationService.createConversation(title);
      return conversation;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      throw error;
    }
  });

  ipcMain.handle('db:conversations:get-all', async () => {
    try {
      const conversations = await conversationService.getAllConversations();
      return conversations;
    } catch (error) {
      console.error('Failed to get conversations:', error);
      throw error;
    }
  });

  ipcMain.handle('db:conversations:get-by-id', async (event, id: string) => {
    try {
      const conversation = await conversationService.getConversationById(id);
      return conversation;
    } catch (error) {
      console.error('Failed to get conversation by id:', error);
      throw error;
    }
  });

  ipcMain.handle('db:conversations:update', async (event, id: string, title: string) => {
    try {
      const conversation = await conversationService.updateConversation(id, { title });
      return conversation;
    } catch (error) {
      console.error('Failed to update conversation:', error);
      throw error;
    }
  });

  ipcMain.handle('db:conversations:delete', async (event, id: string) => {
    try {
      await conversationService.deleteConversation(id);
      return true;
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw error;
    }
  });

  ipcMain.handle('db:conversations:clear-all', async () => {
    try {
      await conversationService.clearAllConversations();
      return true;
    } catch (error) {
      console.error('Failed to clear all conversations:', error);
      throw error;
    }
  });

  // =============================================================================
  // DATABASE OPERATIONS - MESSAGES
  // =============================================================================
    ipcMain.handle('db:messages:create', async (event, messageData: MessageCreate) => {
      try {
          const message = await messageService.createMessage(
            messageData.content,
            stringToMessageRole(messageData.role),
            messageData.conversationId,
            messageData.attachments,
            messageData.error
          );
          return message;
      } catch (error) {
          console.error('Failed to create message:', error);
          throw error;
      }
    });


  ipcMain.handle('db:messages:get-by-conversation', async (event, conversationId: string) => {
    try {
      const messages = await messageService.getMessagesByConversation(conversationId);
      return messages;
    } catch (error) {
      console.error('Failed to get messages by conversation:', error);
      throw error;
    }
  });

  ipcMain.handle('db:messages:update', async (event, id: string, content: string) => {
    try {
      const message = await messageService.updateMessage(id, { content });
      return message;
    } catch (error) {
      console.error('Failed to update message:', error);
      throw error;
    }
  });

  ipcMain.handle('db:messages:delete', async (event, id: string) => {
    try {
      await messageService.deleteMessage(id);
      return true;
    } catch (error) {
      console.error('Failed to delete message:', error);
      throw error;
    }
  });

  ipcMain.handle('db:messages:clear-by-conversation', async (event, conversationId: string) => {
    try {
      await messageService.clearMessagesByConversation(conversationId);
      return true;
    } catch (error) {
      console.error('Failed to clear messages by conversation:', error);
      throw error;
    }
  });

  // =============================================================================
  // FILE SYSTEM OPERATIONS
  // =============================================================================

  ipcMain.handle('fs:save-file', async (event, options: {
    title?: string;
    defaultPath?: string;
    filters?: { name: string; extensions: string[] }[];
    content: string;
  }) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (!window) return null;

    try {
      const result = await dialog.showSaveDialog(window, {
        title: options.title || 'Save File',
        defaultPath: options.defaultPath,
        filters: options.filters || [
          { name: 'JSON Files', extensions: ['json'] },
          { name: 'Text Files', extensions: ['txt'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (!result.canceled && result.filePath) {
        await writeFile(result.filePath, options.content);
        return result.filePath;
      }

      return null;
    } catch (error) {
      console.error('Failed to save file:', error);
      throw error;
    }
  });

  ipcMain.handle('fs:open-file', async (event, options?: {
    title?: string;
    filters?: { name: string; extensions: string[] }[];
    properties?: ('openFile' | 'multiSelections')[];
  }) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (!window) return null;

    try {
      const result = await dialog.showOpenDialog(window, {
        title: options?.title || 'Open File',
        filters: options?.filters || [
          { name: 'JSON Files', extensions: ['json'] },
          { name: 'Text Files', extensions: ['txt'] },
          { name: 'All Files', extensions: ['*'] }
        ],
        properties: options?.properties || ['openFile']
      });

      if (!result.canceled && result.filePaths.length > 0) {
        const filePath = result.filePaths[0];
        const content = await readFile(filePath, 'utf-8');
        return { filePath, content };
      }

      return null;
    } catch (error) {
      console.error('Failed to open file:', error);
      throw error;
    }
  });

  // =============================================================================
  // SYSTEM OPERATIONS
  // =============================================================================

  ipcMain.handle('system:get-app-version', () => {
    return app.getVersion();
  });

  ipcMain.handle('system:get-platform', () => {
    return process.platform;
  });

  ipcMain.handle('system:get-arch', () => {
    return process.arch;
  });

  ipcMain.handle('system:open-external', async (event, url: string) => {
    try {
      await shell.openExternal(url);
      return true;
    } catch (error) {
      console.error('Failed to open external URL:', error);
      return false;
    }
  });

  ipcMain.handle('system:show-item-in-folder', (event, path: string) => {
    shell.showItemInFolder(path);
  });

  ipcMain.handle('system:quit-app', () => {
    app.quit();
  });

  // =============================================================================
  // CLIPBOARD OPERATIONS
  // =============================================================================

  ipcMain.handle('clipboard:write-text', async (event, text: string) => {
    const { clipboard } = require('electron');
    try {
      clipboard.writeText(text);
      return true;
    } catch (error) {
      console.error('Failed to write to clipboard:', error);
      return false;
    }
  });

  ipcMain.handle('clipboard:read-text', () => {
    const { clipboard } = require('electron');
    try {
      return clipboard.readText();
    } catch (error) {
      console.error('Failed to read from clipboard:', error);
      return '';
    }
  });

  // =============================================================================
  // NOTIFICATION OPERATIONS
  // =============================================================================

  ipcMain.handle('notification:show', (event, options: {
    title: string;
    body: string;
    silent?: boolean;
    urgency?: 'normal' | 'critical' | 'low';
  }) => {
    const { Notification } = require('electron');
    
    if (Notification.isSupported()) {
      const notification = new Notification({
        title: options.title,
        body: options.body,
        silent: options.silent || false,
        urgency: options.urgency || 'normal'
      });
      
      notification.show();
      return true;
    }
    
    return false;
  });

  // =============================================================================
  // DIALOG OPERATIONS
  // =============================================================================

  ipcMain.handle('dialog:show-message', async (event, options: {
    type?: 'none' | 'info' | 'error' | 'question' | 'warning';
    title?: string;
    message: string;
    detail?: string;
    buttons?: string[];
    defaultId?: number;
    cancelId?: number;
  }) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (!window) return { response: -1 };

    try {
      const result = await dialog.showMessageBox(window, {
        type: options.type || 'info',
        title: options.title || 'Message',
        message: options.message,
        detail: options.detail,
        buttons: options.buttons || ['OK'],
        defaultId: options.defaultId || 0,
        cancelId: options.cancelId
      });

      return result;
    } catch (error) {
      console.error('Failed to show message dialog:', error);
      return { response: -1 };
    }
  });

  ipcMain.handle('dialog:show-error', async (event, title: string, content: string) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (!window) return;

    try {
      await dialog.showErrorBox(title, content);
    } catch (error) {
      console.error('Failed to show error dialog:', error);
    }
  });


  // =============================================================================
  // HOTKEY MANAGEMENT
  // =============================================================================

  ipcMain.handle('hotkeys:get-settings', async () => {
    return hotkeyService.getSettings();
  });

  ipcMain.handle('hotkeys:save-settings', async (event, settings: Partial<HotkeySettings>) => {
    try {
      await hotkeyService.saveAndReloadHotkeys(settings);
      return { success: true };
    } catch (error) {
      console.error('Failed to save hotkey settings:', error);
      return { success: false, error: (error as Error).message };
    }
  });
  
  ipcMain.handle('hotkeys:register-all', async () => {
      hotkeyService.registerAll();
  });


  // Placeholder for recording functionality. A real implementation might need a dedicated window.
  ipcMain.handle('hotkeys:start-recording', async (event) => {
    console.log("IPC: Start hotkey recording requested.");
    return null; 
  });

  ipcMain.handle('hotkeys:stop-recording', async () => {
    console.log("IPC: Stop hotkey recording requested.");
  });


  ipcMain.handle('provider:add', async (event, providerData: Omit<LLMProvider, 'id'>): Promise<IPCResponse<LLMProvider>> => {
    try {
      const newProvider = await configService.addLLMProvider(providerData);
      return { success: true, data: newProvider };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('provider:update', async (event, provider: LLMProvider): Promise<IPCResponse<void>> => {
    try {
      await configService.updateLLMProvider(provider);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('provider:delete', async (event, providerId: string): Promise<IPCResponse<void>> => {
    try {
      await configService.deleteLLMProvider(providerId);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  });

  ipcMain.handle('provider:set-default', async (event, providerId: string): Promise<IPCResponse<void>> => {
    try {
      await configService.setDefaultLLMProvider(providerId);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  });

  // =============================================================================
  // DEVELOPMENT HELPERS
  // =============================================================================

  ipcMain.handle('dev:open-devtools', (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window && process.env.NODE_ENV === 'development') {
      window.webContents.openDevTools();
    }
  });

  ipcMain.handle('dev:reload', (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (window && process.env.NODE_ENV === 'development') {
      window.webContents.reload();
    }
  });

  // =============================================================================
  // ERROR HANDLING
  // =============================================================================

  ipcMain.handle('log:error', (event, error: any) => {
    console.error('Renderer Error:', error);
  });

  ipcMain.handle('log:info', (event, message: string) => {
    console.log('Renderer Info:', message);
  });

  ipcMain.handle('log:warn', (event, message: string) => {
    console.warn('Renderer Warning:', message);
  });

  console.log('IPC handlers registered successfully');
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

export function removeIpcHandlers(): void {
  // Remove all registered IPC handlers
  const handlers = [
    // Window management
    'window:resize', 'window:hide', 'window:show', 'window:minimize', 'window:close', 'window:set-always-on-top',
    
    // Configuration
    'config:load', 'config:save', 'config:get-path',
    
    // Database - Conversations
    'db:conversations:create', 'db:conversations:get-all', 'db:conversations:get-by-id',
    'db:conversations:update', 'db:conversations:delete', 'db:conversations:clear-all',
    
    // Database - Messages
    'db:messages:create', 'db:messages:get-by-conversation', 'db:messages:update',
    'db:messages:delete', 'db:messages:clear-by-conversation',
    
    // File system
    'fs:save-file', 'fs:open-file',
    
    // System
    'system:get-app-version', 'system:get-platform', 'system:get-arch',
    'system:open-external', 'system:show-item-in-folder', 'system:quit-app',
    
    // Clipboard
    'clipboard:write-text', 'clipboard:read-text',
    
    // Notifications
    'notification:show',
    
    // Dialogs
    'dialog:show-message', 'dialog:show-error',
    
    // Development
    'dev:open-devtools', 'dev:reload',
    
    // Logging
    'log:error', 'log:info', 'log:warn'
  ];

  handlers.forEach(handler => {
    ipcMain.removeHandler(handler);
  });

  console.log('IPC handlers removed');
}