import { Attachment } from "@shared/types";

export { Attachment } from "@shared/types";

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export function stringToMessageRole(role: string): MessageRole {
  switch (role.toLowerCase()) {
    case 'user':
      return MessageRole.USER;
    case 'assistant':
      return MessageRole.ASSISTANT;
    case 'system':
      return MessageRole.SYSTEM;
    default:
      throw new Error(`Invalid message role: ${role}`);
  }
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messages?: Message[];
  isArchived: boolean;
}

export interface Message {
  id: string;
  content: string;
  attachments?: Attachment[];
  error?: string;
  role: MessageRole;
  conversationId: string;
  createdAt: Date;
  conversation?: {
      id: string;
      title: string;
  };}

export interface MessageCreate {
      content: string;
      role: MessageRole;
      conversationId: string;
      attachments?: Attachment[];
      error?: string;
}

// Generated types from Prisma schema
export interface ConversationSummary {
  id: string;
  title: string;
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

// Database service events
export interface DatabaseEvents {
  'initialized': () => void;
  'error': (error: Error) => void;
  'backup-created': (path: string) => void;
  'data-cleared': () => void;
}


export const isMessageRole = (role: string): role is MessageRole => {
  return Object.values(MessageRole).includes(role as MessageRole);
};

export const isValidMessage = (obj: any): obj is Message => {
  return (
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.content === 'string' &&
    isMessageRole(obj.role) &&
    typeof obj.conversationId === 'string' &&
    obj.createdAt instanceof Date
  );
};