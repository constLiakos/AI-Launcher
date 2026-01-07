import { contextBridge, ipcRenderer } from 'electron';
import { ElectronAPI, Settings, HotkeySettings, LLMProvider, IPCResponse, AIMessage, AIStreamChunk, Model, MessageRole, Attachment } from '@shared/types';
import { AppConfig } from '@shared/config/AppConfig';
import { MessageCreate } from '@shared/database-types';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
const electronAPI: ElectronAPI = {
  // Window management
  resizeWindow: (width: number|null, height: number|null) => 
    ipcRenderer.invoke('window:resize', width, height),
  hideWindow: () => 
    ipcRenderer.invoke('window:hide'),
  showWindow: () => 
    ipcRenderer.invoke('window:show'),
  minimizeWindow: () => 
    ipcRenderer.invoke('window:minimize'),

  // Settings-specific IPC calls
  loadConfig: () => 
    ipcRenderer.invoke('config:load'),
  saveConfig: (config: Partial<AppConfig>) => 
    ipcRenderer.invoke('config:save', config),
  resetConfig: () => ipcRenderer.invoke('config:reset'),
  exportConfig: () => ipcRenderer.invoke('config:export'),
  importConfig: (configJson: string) => ipcRenderer.invoke('config:import', configJson),
  onConfigUpdate: (callback: (config: Partial<AppConfig>) => void) => {
    const handler = (_event: any, config: Partial<AppConfig>) => callback(config);
    ipcRenderer.on('config-updated', handler);
    return () => {
      ipcRenderer.removeListener('config-updated', handler);
    };
  },
  // UI Interaction
  onFocusInput: (callback: () => void) => {
    ipcRenderer.on('focus-input', callback);
    // Return a cleanup function
    return () => {
      ipcRenderer.removeListener('focus-input', callback);
    };
  },

  fetchAvailableModels: (provider: LLMProvider): Promise<IPCResponse<Model[]>> =>
    ipcRenderer.invoke('ai:fetch-models', provider),
  // Provider Management
  addProvider: (providerData: Omit<LLMProvider, 'id'>) => ipcRenderer.invoke('provider:add', providerData),
  updateProvider: (provider: LLMProvider) => ipcRenderer.invoke('provider:update', provider),
  deleteProvider: (providerId: string) => ipcRenderer.invoke('provider:delete', providerId),
  setDefaultProvider: (providerId: string) => ipcRenderer.invoke('provider:set-default', providerId),

  // AI Service
  generateAIResponse: (messages: AIMessage[]) => 
    ipcRenderer.invoke('ai:generate-response', messages),
  generateAIStream: (payload: { messages: AIMessage[], tempMessageId: string, modelId: string, providerId: string }) => 
    ipcRenderer.invoke('ai:generate-stream', payload),
  downloadAttachment: (args: { dataUrl: string, filename: string }) => ipcRenderer.invoke('download-attachment', args),
  processPdfAttachment: (dataUrl: string) => ipcRenderer.invoke('process-pdf-attachment', dataUrl),
  onAIStreamChunk: (callback) => {
    const handler = (_event: any, chunk: AIStreamChunk) => callback(chunk);
    ipcRenderer.on('ai:stream-chunk', handler);
    return () => {
      ipcRenderer.removeListener('ai:stream-chunk', handler);
    };
  },
  // File operations for import/export
  saveFile: (options: any) => ipcRenderer.invoke('fs:save-file', options),
  openFile: (options: any) => ipcRenderer.invoke('fs:open-file', options),

  onSettingsOpen: () => 
    ipcRenderer.invoke('settings:open'),
  saveSettings: (settings: Settings) =>
    ipcRenderer.invoke('settings:save', settings),

  // Database operations - Conversations
  createConversation: (title: string) => 
    ipcRenderer.invoke('db:conversations:create', title),
  getAllConversations: () => 
    ipcRenderer.invoke('db:conversations:get-all'),
  getConversationById: (id: string) => 
    ipcRenderer.invoke('db:conversations:get-by-id', id),
  updateConversation: (id: string, title: string) => 
    ipcRenderer.invoke('db:conversations:update', id, title),
  deleteConversation: (id: string) => 
    ipcRenderer.invoke('db:conversations:delete', id),
  clearAllConversations: () =>
    ipcRenderer.invoke('db:conversations:clear-all'),
  clearMessagesByConversation: (conversationId: string) =>
    ipcRenderer.invoke('db:messages:clear-by-conversation', conversationId),
  // Database operations - Messages
  createMessage: (payload: MessageCreate) => 
    ipcRenderer.invoke('db:messages:create', payload),
  getMessagesByConversation: (conversationId: string) => 
    ipcRenderer.invoke('db:messages:get-by-conversation', conversationId),
  updateMessage: (id: string, content: string) => 
    ipcRenderer.invoke('db:messages:update', id, content),
  deleteMessage: (id: string) => 
    ipcRenderer.invoke('db:messages:delete', id),
  getScreenSources: () => ipcRenderer.invoke('get-screen-sources'),
  captureHighResSource: (sourceId: string) => ipcRenderer.invoke('capture-high-res-source', sourceId),
  sttTranscribe: (audioData: Uint8Array): Promise<string> => {
    return ipcRenderer.invoke('stt:transcribe', audioData);
  },

  // System operations
  openExternal: (url: string) => 
    ipcRenderer.invoke('system:open-external', url),
  showNotification: (title: string, body: string) => 
    ipcRenderer.invoke('notification:show', { title, body }),

  showContextMenu: () => ipcRenderer.invoke('system:show-context-menu'),

  // Clipboard
  writeToClipboard: (text: string) => 
    ipcRenderer.invoke('clipboard:write-text', text),
  readFromClipboard: () => 
    ipcRenderer.invoke('clipboard:read-text'),

  // Hotkey management
  getHotkeySettings: () => 
    ipcRenderer.invoke('hotkeys:get-settings'),
  saveHotkeySettings: (settings: Partial<HotkeySettings>) =>
    ipcRenderer.invoke('hotkeys:save-settings', settings),
  registerHotkeys: () => 
    ipcRenderer.invoke('hotkeys:register-all'),
  startHotkeyRecording: () => 
    ipcRenderer.invoke('hotkeys:start-recording'),
  stopHotkeyRecording: () => 
    ipcRenderer.invoke('hotkeys:stop-recording'),

  // // System information
  getAppVersion: () => ipcRenderer.invoke('system:get-app-version'),
  // getPlatform: () => ipcRenderer.invoke('system:get-platform'),

  // // File operations for import/export
  // saveFile: (options: any) => ipcRenderer.invoke('fs:save-file', options),
  // openFile: (options: any) => ipcRenderer.invoke('fs:open-file', options),

  // // Listen for main process events

};

contextBridge.exposeInMainWorld('electronAPI', electronAPI);
