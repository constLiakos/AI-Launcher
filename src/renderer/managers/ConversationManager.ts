// src/renderer/managers/ConversationManager.ts
import { Attachment, Conversation, Message, MessageRole } from '@shared/types';
import { v4 as uuidv4 } from 'uuid';

/**
 * Manages the state of conversations in the renderer process.
 * Acts as the single source of truth for the active conversation.
 */
export class ConversationManager {
  private activeConversation: Conversation | null = null;
  private static instance: ConversationManager;

  // Singleton pattern to ensure only one manager instance
  public static getInstance(): ConversationManager {
    if (!ConversationManager.instance) {
      ConversationManager.instance = new ConversationManager();
    }
    return ConversationManager.instance;
  }

  /**
   * Loads a conversation from the database or creates a new temporary one in memory.
   */
  public async loadOrCreateConversation(conversationId?: string): Promise<Conversation> {
    if (conversationId) {
      const conversation = await window.electronAPI.getConversationById(conversationId);
      if (conversation) {
        this.activeConversation = conversation;
        return conversation;
      }
    }
    
    // If no ID or conversation not found, create a new temporary one
    return this.createNewConversation();
  }

  /**
   * Creates a new, temporary conversation in-memory without saving it to the database.
   * It is only saved when the first message is added.
   * @returns The new temporary conversation object.
   */
  public createNewConversation(): Conversation {
    const tempId = `temp-${uuidv4()}`;
    const newConversation: Conversation = {
      id: tempId,
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      isArchived: false,
    };
    
    this.activeConversation = newConversation;
    return newConversation;
  }

  // Loads a conversation and sets it as active
  public async loadAndSetActiveConversation(conversationId: string): Promise<Conversation | null> {
    const conversation = await window.electronAPI.getConversationById(conversationId);
    if (conversation) {
        this.activeConversation = conversation;
    }
    return conversation;
  }

  public async getAllConversations(): Promise<Conversation[]> {
    return await window.electronAPI.getAllConversations();
  }
  
  public async deleteConversation(conversationId: string): Promise<void> {
    await window.electronAPI.deleteConversation(conversationId);
    if (this.activeConversation?.id === conversationId) {
        this.createNewConversation();
    }
  }
  public async clearAllConversations(): Promise<void> {
    await window.electronAPI.clearAllConversations();
    this.createNewConversation();
  }
  /**
   * Returns the currently active conversation.
   */
  public getActiveConversation(): Conversation | null {
    return this.activeConversation;
  }

  /**
   * Returns the messages of the active conversation.
   */
  public getActiveMessages(): Message[] {
    return this.activeConversation?.messages || [];
  }

  /**
   * Adds a message to the current conversation.
   * If the conversation is temporary, it first creates it in the database.
   * @param content The text content of the message.
   * @param role The role of the message sender.
   * @returns The newly created message.
   */

  public async addMessage(
    content: string, 
    role: MessageRole, 
    attachments?: Attachment[]
  ): Promise<Message> {
    if (!this.activeConversation) {
      throw new Error('No active conversation to add a message to.');
    }

    const isTemporary = this.activeConversation.id.startsWith('temp-');

    if (isTemporary && this.activeConversation.messages.length === 0) {
      const newTitle = content.substring(0, 40) + (content.length > 40 ? '...' : '');
      const savedConversation = await window.electronAPI.createConversation(newTitle);
      
      this.activeConversation = savedConversation;
    }

    if (!this.activeConversation) {
        throw new Error('Failed to create or retrieve the conversation from the database.');
    }

    const newMessage =  await window.electronAPI.createMessage({
      content,
      role,
      conversationId: this.activeConversation.id,
      attachments
    });

    this.activeConversation.messages.push(newMessage);
    return newMessage;
  }

  public async finalizeAssistantMessage(tempId: string, finalContent: string, error?: string): Promise<void> {
    const conversation = this.getActiveConversation();
    if (!conversation) return;
    let new_msg;
    if (error != undefined){
      new_msg = {
        content:"error",
        role:MessageRole.ASSISTANT,
        conversationId:conversation.id,
        error: error
      }
    }else{
      new_msg = {
        content: finalContent,
        role:MessageRole.ASSISTANT,
        conversationId:conversation.id
      }
    }
    const finalMessage =  await window.electronAPI.createMessage(new_msg);
    
    const messageIndex = conversation.messages.findIndex(m => m.id === tempId);
    if (messageIndex !== -1) {
      conversation.messages[messageIndex] = finalMessage;
    }
  }

  /**
    * Clears all messages from the current conversation in the UI and database.
    */
  public async clearActiveConversationMessages(): Promise<void> {
    if (!this.activeConversation) return;

    if (this.activeConversation.id.startsWith('temp-')) {
        this.activeConversation.messages = [];
        return;
    }

    await window.electronAPI.clearMessagesByConversation(this.activeConversation.id);

    this.activeConversation.messages = [];
  }

  /**
   * Adds an assistant message with an error to the current conversation.
   * @param tempId The temporary ID of the message to replace.
   * @param errorContent The error message.
   */
  public async addErrorMessage(tempId: string, errorContent: string): Promise<void> {
    const conversation = this.getActiveConversation();
    if (!conversation) return;

    // Create the message with the error field
    const errorMessage = await window.electronAPI.createMessage({
      content: 'An error occurred.',
      role: MessageRole.ASSISTANT,
      conversationId: conversation.id,
      error: errorContent,
    });

    // Replace the temporary placeholder message with the final error message
    const messageIndex = conversation.messages.findIndex(m => m.id === tempId);
    if (messageIndex !== -1) {
      conversation.messages[messageIndex] = errorMessage;
    }
  }
}