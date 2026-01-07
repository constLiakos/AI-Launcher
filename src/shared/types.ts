// src/shared/types.ts

import { AppConfig } from '@shared/config/AppConfig';
import { PdfProcessingStrategy } from "@main/services/AttachmentService";
import { MessageCreate } from "@shared/database-types";

// =============================================================================
// ENUMS
// =============================================================================

export interface Preferences {
  autostart: boolean;
  showDockIcon: boolean;
  confirmOnQuit: boolean;
  confirmOnDelete: boolean;
}

export enum STTProviderType {
  OPENAI = 'openai',
  // Placeholder for future providers
}

export interface STTSettings {
  enabled: boolean;
  provider: STTProviderType;
  apiBase: string;
  apiKey: string;
  model: string;
  timeout: number;
}

export interface Model {
  id: string; // e.g., 'gpt-4o-mini'
  name: string; // e.g., 'GPT-4o Mini'
  providerType: LLMProviderType; // e.g., 'openai'
  providerId: string; // ID του provider instance
}

export enum LLMProviderType {
  OPENAI = 'openai',
  GROQ = 'groq',
  TOGETHER = 'together',
  FIREWORKS = 'fireworks',
  OLLAMA = 'ollama',
}

export interface LLMProvider {
  id: string;
  name: string;
  type: LLMProviderType;
  apiKey: string;
  apiBase: string;
  timeout: number;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  availableModels?: Model[];
  customModels?: Model[];
}

export interface AIStreamChunk {
  tempMessageId: string;
  content?: string;
  isFinal: boolean;
  error?: string;
}

export interface ConversationSettings {
  historyLimit: number;
  clearHistoryOnMinimize: boolean;
  clearLastResponseOnMinimize: boolean;
  pdfProcessingStrategy: PdfProcessingStrategy
}

export interface WindowSettings {
  dimensions: WindowDimensions;
  alwaysOnTop: boolean;
  startMinimized: boolean;
  frame: boolean;
  transparent: boolean;
  resizable: boolean;
}

export interface WindowStateData {
  position: { x: number; y: number } | null;
  rememberedBounds: { x: number; y: number; width: number; height: number } | null;
}

export enum InputMode {
  SINGLE_LINE = 'single',
  MULTI_LINE = 'multi'
}

export enum RecordingState {
  IDLE = 'idle',
  RECORDING = 'recording',
  PROCESSING = 'processing'
}

export enum WindowState {
  COMPACT = 'compact',
  EXPANDED = 'expanded'
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

// =============================================================================
// HOTKEY TYPES
// =============================================================================

/**
 * Defines the available actions that can be triggered by a hotkey.
 */
export enum HotkeyAction {
  ToggleWindow = 'toggle-window',
  OpenSettings = 'open-settings',
  StartRecording = 'start-recording',
}

/**
 * Represents a single hotkey configuration.
 */
export interface HotkeyConfig {
  /** A unique identifier for the hotkey action. */
  action: HotkeyAction;
  /** The key combination (e.g., 'CommandOrControl+Shift+A'). Can be null if not set. */
  accelerator: string | null;
  /** A user-friendly description of the hotkey's function. */
  label: string;
  /** Whether the hotkey can be modified by the user. */
  isEditable: boolean;
}

export type HotkeySettings = {
  [key in HotkeyAction]: HotkeyConfig;
};

/**
 * Represents the complete set of hotkey settings for the application.
 * It's a dictionary-like type where each key is a HotkeyAction,
 * and the value is the corresponding HotkeyConfig.
 */


// =============================================================================
// INTERFACES
// =============================================================================

export interface AppState {
  inputMode: InputMode;
  recordingState: RecordingState;
  windowState: WindowState;
  isConversationVisible: boolean;
}

export interface WindowDimensions {
  width: number;
  height: number;
  minWidth: number;
  minHeight: number;
}

export interface ImageAttachment {
  type: 'image';
  data: string;
}

export interface PDFAttachment {
  type: 'pdf';
  data: string;
  filename: string;
  extractedText?: string;
}

export interface ScreenCaptureAttachment {
  type: 'screen-capture';
  data: string;
  sourceId: string;
}


export type Attachment = ImageAttachment | ScreenCaptureAttachment | PDFAttachment;

// =============================================================================
// DATABASE TYPES (ΕΝΗΜΕΡΩΜΕΝΟ)
// =============================================================================

export interface Message {
  id: string;
  content: string;
  attachments?: Attachment[];
  error?: string;
  role: MessageRole;
  conversationId: string;
  createdAt: Date;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages: Message[];
  isArchived: boolean;
}

export interface DatabaseStats {
  conversationCount: number;
  messageCount: number;
  databaseSize: string;
  lastModified: Date | null;
}

export interface DatabaseHealthCheck {
  connected: boolean;
  tablesExist: boolean;
  canWrite: boolean;
  errors: string[];
}

// =============================================================================
// IPC TYPES
// =============================================================================

export interface IPCResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// =============================================================================
// AI SERVICE TYPES
// =============================================================================

export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string | Array<{ type: 'text'; text: string } | { type: 'image_url'; image_url: { url: string } }>;
  attachments?: Attachment[];
}

export interface PdfProcessSuccessResponse {
  success: true;
  data: {
    extractedText: string | null;
  };
}

export interface PdfProcessErrorResponse {
  success: false;
  error: string;
}

export type PdfProcessResponse = PdfProcessSuccessResponse | PdfProcessErrorResponse;

// =============================================================================
// CONFIGURATION TYPES
// =============================================================================

export interface STTSettings {
  enabled: boolean;
  apiBase: string;
  model: string;
  timeout: number;
}

export interface Settings extends Partial<AppConfig> {}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export type MessageContent = string;
export type ConversationID = string;
export type MessageID = string;

// =============================================================================
// EVENT TYPES
// =============================================================================

// export interface AppEvents {
//   'conversation-created': Conversation;
//   'conversation-updated': Conversation;
//   'conversation-deleted': string;
//   'message-created': Message;
//   'message-updated': Message;
//   'message-deleted': string;
//   'window-state-changed': WindowState;
//   'recording-state-changed': RecordingState;
//   'input-mode-changed': InputMode;
// }

// =============================================================================
// ELECTRON API TYPES
// =============================================================================


export interface ElectronAPI {
  loadConfig: () => Promise<AppConfig>;
  saveConfig: (config: any) => Promise<void>;
  saveSettings: (settings: Settings) => Promise<IPCResponse<void>>;
  resetConfig: () => Promise<IPCResponse<void>>;
  exportConfig: () => Promise<IPCResponse<{ path: string }>>;
  importConfig: (configJson: string) => Promise<IPCResponse<void>>;
  onConfigUpdate: (callback: (config: Partial<AppConfig>) => void) => void;

  generateAIResponse: (messages: AIMessage[]) => Promise<string>;
  generateAIStream: (payload: { messages: AIMessage[], tempMessageId: string, modelId: string, providerId: string }) => void;
  onAIStreamChunk: (callback: (chunk: AIStreamChunk) => void) => () => void;
  clearMessagesByConversation: (conversationId: string) => Promise<void>; 
  clearAllConversations: () => Promise<void>; 
  fetchAvailableModels: (provider: LLMProvider) => Promise<IPCResponse<Model[]>>;
  sttTranscribe: (audioData: Uint8Array) => Promise<string>;

  addProvider: (providerData: Omit<LLMProvider, 'id'>) => Promise<IPCResponse<LLMProvider>>;
  updateProvider: (provider: LLMProvider) => Promise<IPCResponse<void>>;
  deleteProvider: (providerId: string) => Promise<IPCResponse<void>>;
  setDefaultProvider: (providerId: string) => Promise<IPCResponse<void>>;
  onFocusInput: (callback: () => void) => () => void;
  resizeWindow: (width: number|null, height: number|null) => void;
  hideWindow: () => void;
  showWindow: () => void;
  minimizeWindow: () => void;
  getAppVersion: () => Promise<string>;

  createConversation: (title: string) => Promise<any>;
  getAllConversations: () => Promise<any[]>;
  getConversationById: (id: string) => Promise<any | null>;
  updateConversation: (id: string, title: string) => Promise<any>;
  deleteConversation: (id: string) => Promise<void>;
  createMessage: (payload: MessageCreate) => Promise<any>;
  getMessagesByConversation: (conversationId: string) => Promise<any[]>;
  updateMessage: (id: string, content: string) => Promise<any>;
  deleteMessage: (id: string) => Promise<void>;
  downloadAttachment: (args: { dataUrl: string, filename: string }) => Promise<void>;
  processPdfAttachment: (dataUrl: string) => Promise<PdfProcessResponse>;
  getHotkeySettings: () => Promise<HotkeySettings>;
  saveHotkeySettings: (settings: Partial<HotkeySettings>) => Promise<IPCResponse<void>>;
  registerHotkeys: () => Promise<void>;
  startHotkeyRecording: () => Promise<string | null>;
  stopHotkeyRecording: () => void;
  getScreenSources: () => Promise<ScreenSource[]>;
  captureHighResSource: (sourceId: string) => Promise<string>;


  showContextMenu: () => Promise<void>;
  openExternal: (url: string) => Promise<void>;
  showNotification: (title: string, body: string) => Promise<void>;
  writeToClipboard: (text: string) => Promise<boolean>;
  readFromClipboard: () => Promise<string>;
  
  saveFile: (options: {
    title?: string;
    defaultPath?: string;
    filters?: { name: string; extensions: string[] }[];
    content: string;
  }) => Promise<string | null>;

  openFile: (options?: {
    title?: string;
    filters?: { name: string; extensions: string[] }[];
    properties?: ('openFile' | 'multiSelections')[];
  }) => Promise<{ filePath: string; content: string } | null>;

  onSettingsOpen: () => void;
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

export interface ScreenSource {
  id: string;
  name: string;
  thumbnail: string;
}