import { DatabaseService } from '@main/services/DatabaseService';
import { PrismaClient, Message as PrismaMessage, Conversation, Prisma } from 'generated/client';
import type { Message, MessageRole } from '@shared/database-types';
import { stringToMessageRole } from '@shared/database-types';
import { ConversationService } from '@main/services/ConversationService';
import { Attachment } from '@shared/types';

// Define the type for a message as returned by Prisma, including the conversation relation
type MessageWithConversation = PrismaMessage & {
  conversation?: Conversation;
};

export class MessageService {
  private db: PrismaClient;
  private conversationService: ConversationService;

  constructor(databaseService: DatabaseService, conversationService: ConversationService) {
    this.db = databaseService.getClient();
    this.conversationService = conversationService;
  }

  /**
   * Create a new message
   */
    async createMessage(
    content: string,
    role: MessageRole,
    conversationId: string,
    attachments?: Attachment[],
    error?: string
  ): Promise<Message> {
    try {
      // Validate conversation exists
      const conversationExists = await this.conversationService.conversationExists(conversationId);
      if (!conversationExists) {
        throw new Error('Conversation not found');
      }

      const message = await this.db.message.create({
        data: {
          content: content.trim(),
          role,
          conversationId,
          createdAt: new Date(),
          error: error,
          attachments:
            attachments && attachments.length > 0
              ? (attachments as unknown as Prisma.InputJsonValue)
              : undefined,
        },
        include: {
          conversation: true
        }
      });

      // Update conversation timestamp
      await this.conversationService.touchConversation(conversationId);

      console.log(`Created message: ${message.id} with ${attachments?.length || 0} attachments in conversation: ${conversationId}`);
      return this.mapMessage(message);
    } catch (error) {
      console.error('Failed to create message:', error);
      throw new Error(`Failed to create message: ${error}`);
    }
  }


  /**
   * Get all messages for a conversation
   */
  async getMessagesByConversation(
    conversationId: string,
    limit?: number,
    offset?: number
  ): Promise<Message[]> {
    try {
      const messages = await this.db.message.findMany({
        where: {
          conversationId
        },
        orderBy: {
          createdAt: 'asc'
        },
        ...(limit && { take: limit }),
        ...(offset && { skip: offset }),
        include: {
          conversation: true
        }
      });

      return messages.map((msg) => this.mapMessage(msg));
    } catch (error) {
      console.error('Failed to get messages by conversation:', error);
      throw new Error(`Failed to get messages: ${error}`);
    }
  }

  /**
   * Get recent messages for a conversation
   */
  async getRecentMessages(
    conversationId: string,
    limit: number = 10
  ): Promise<Message[]> {
    try {
      const messages = await this.db.message.findMany({
        where: {
          conversationId
        },
        orderBy: {
          createdAt: 'desc'
        },
        take: limit,
        include: {
          conversation: true
        }
      });

      // Reverse to get chronological order
      return messages.reverse().map((msg) => this.mapMessage(msg));
    } catch (error) {
      console.error('Failed to get recent messages:', error);
      throw new Error(`Failed to get recent messages: ${error}`);
    }
  }

  /**
   * Get message by ID
   */
  async getMessageById(id: string): Promise<Message | null> {
    try {
      const message = await this.db.message.findUnique({
        where: { id },
        include: {
          conversation: true
        }
      });

      if (!message) {
        return null;
      }

      return this.mapMessage(message);
    } catch (error) {
      console.error('Failed to get message by ID:', error);
      throw new Error(`Failed to get message: ${error}`);
    }
  }

  /**
   * Update message content
   */
  async updateMessage(
    id: string,
    data: { content?: string; role?: MessageRole }
  ): Promise<Message> {
    try {
      const message = await this.db.message.update({
        where: { id },
        data: {
          ...data,
          ...(data.content && { content: data.content.trim() })
        },
        include: {
          conversation: true
        }
      });

      // Update conversation timestamp
      await this.conversationService.touchConversation(message.conversationId);

      console.log(`Updated message: ${message.id}`);
      return this.mapMessage(message);
    } catch (error) {
      console.error('Failed to update message:', error);
      throw new Error(`Failed to update message: ${error}`);
    }
  }

  /**
   * Delete message
   */
  async deleteMessage(id: string): Promise<void> {
    try {
      const message = await this.db.message.findUnique({
        where: { id },
        select: { conversationId: true }
      });

      if (!message) {
        throw new Error('Message not found');
      }

      await this.db.message.delete({
        where: { id }
      });

      // Update conversation timestamp
      await this.conversationService.touchConversation(message.conversationId);

      console.log(`Deleted message: ${id}`);
    } catch (error) {
      console.error('Failed to delete message:', error);
      throw new Error(`Failed to delete message: ${error}`);
    }
  }

  /**
   * Delete multiple messages
   */
  async deleteMessages(ids: string[]): Promise<number> {
    try {
      const result = await this.db.message.deleteMany({
        where: {
          id: {
            in: ids
          }
        }
      });

      console.log(`Deleted ${result.count} messages`);
      return result.count;
    } catch (error) {
      console.error('Failed to delete messages:', error);
      throw new Error(`Failed to delete messages: ${error}`);
    }
  }

  /**
   * Clear all messages from a conversation
   */
  async clearMessagesByConversation(conversationId: string): Promise<void> {
    try {
      const result = await this.db.message.deleteMany({
        where: {
          conversationId
        }
      });

      console.log(`Cleared ${result.count} messages from conversation: ${conversationId}`);
    } catch (error) {
      console.error('Failed to clear messages by conversation:', error);
      throw new Error(`Failed to clear messages: ${error}`);
    }
  }

  /**
   * Get message count for a conversation
   */
  async getMessageCount(conversationId: string): Promise<number> {
    try {
      return await this.db.message.count({
        where: {
          conversationId
        }
      });
    } catch (error) {
      console.error('Failed to get message count:', error);
      throw new Error(`Failed to get message count: ${error}`);
    }
  }


  /**
   * Get messages by role
   */
  async getMessagesByRole(
    conversationId: string,
    role: MessageRole
  ): Promise<Message[]> {
    try {
      const messages = await this.db.message.findMany({
        where: {
          conversationId,
          role
        },
        orderBy: {
          createdAt: 'asc'
        },
        include: {
          conversation: true
        }
      });

      return messages.map((msg) => this.mapMessage(msg));
    } catch (error) {
      console.error('Failed to get messages by role:', error);
      throw new Error(`Failed to get messages by role: ${error}`);
    }
  }

  /**
   * Search messages by content
   */
  async searchMessages(
    query: string,
    conversationId?: string
  ): Promise<Message[]> {
    try {
      const messages = await this.db.message.findMany({
        where: {
          content: {
            contains: query
          },
          ...(conversationId && { conversationId })
        },
        orderBy: {
          createdAt: 'desc'
        },
        include: {
          conversation: true
        }
      });

      return messages.map((msg) => this.mapMessage(msg));
    } catch (error) {
      console.error('Failed to search messages:', error);
      throw new Error(`Failed to search messages: ${error}`);
    }
  }

  /**
   * Get conversation context (recent messages for AI)
   */
  async getConversationContext(
    conversationId: string,
    maxMessages: number = 20
  ): Promise<Message[]> {
    try {
      const messages = await this.db.message.findMany({
        where: {
          conversationId
        },
        orderBy: {
          createdAt: 'desc'
        },
        take: maxMessages,
        include: {
          conversation: true
        }
      });

      // Return in chronological order
      return messages.reverse().map((msg) => this.mapMessage(msg));
    } catch (error) {
      console.error('Failed to get conversation context:', error);
      throw new Error(`Failed to get conversation context: ${error}`);
    }
  }

  /**
   * Create multiple messages (batch)
   */
  async createMessages(
    messagesData: Array<{
      content: string;
      role: MessageRole;
      conversationId: string;
    }>
  ): Promise<Message[]> {
    try {
      const messages = await this.db.$transaction(
        messagesData.map(data =>
          this.db.message.create({
            data: {
              content: data.content.trim(),
              role: data.role,
              conversationId: data.conversationId,
              createdAt: new Date()
            },
            include: {
              conversation: true
            }
          })
        )
      );

      // Update conversation timestamps
      const conversationIds = [...new Set(messagesData.map(m => m.conversationId))];
      await Promise.all(
        conversationIds.map(id => this.conversationService.touchConversation(id))
      );

      console.log(`Created ${messages.length} messages in batch`);
      return messages.map((msg) => this.mapMessage(msg));
    } catch (error) {
      console.error('Failed to create messages batch:', error);
      throw new Error(`Failed to create messages batch: ${error}`);
    }
  }

  /**
   * Get last message from conversation
   */
  async getLastMessage(conversationId: string): Promise<Message | null> {
    try {
      const message = await this.db.message.findFirst({
        where: {
          conversationId
        },
        orderBy: {
          createdAt: 'desc'
        },
        include: {
          conversation: true
        }
      });

      if (!message) {
        return null;
      }

      return this.mapMessage(message);
    } catch (error) {
      console.error('Failed to get last message:', error);
      throw new Error(`Failed to get last message: ${error}`);
    }
  }

  /**
   * Get first message from conversation
   */
  async getFirstMessage(conversationId: string): Promise<Message | null> {
    try {
      const message = await this.db.message.findFirst({
        where: {
          conversationId
        },
        orderBy: {
          createdAt: 'asc'
        },
        include: {
          conversation: true
        }
      });

      if (!message) {
        return null;
      }

      return this.mapMessage(message);
    } catch (error) {
      console.error('Failed to get first message:', error);
      throw new Error(`Failed to get first message: ${error}`);
    }
  }

  /**
   * Map database message to application type
   */

  private mapMessage(dbMessage: MessageWithConversation): Message {
    const message: Message = {
        id: dbMessage.id,
        content: dbMessage.content,
        attachments: dbMessage.attachments ? (dbMessage.attachments as unknown as Attachment[]) : [],
        role: stringToMessageRole(dbMessage.role),
        conversationId: dbMessage.conversationId,
        createdAt: dbMessage.createdAt,
    };

    if (dbMessage.conversation) {
        message.conversation = {
            id: dbMessage.conversation.id,
            title: dbMessage.conversation.title,
        };
    }

    return message;
  }

  /**
   * Check if message exists
   */
  async messageExists(id: string): Promise<boolean> {
    try {
      const count = await this.db.message.count({
        where: { id }
      });
      return count > 0;
    } catch (error) {
      console.error('Failed to check message existence:', error);
      return false;
    }
  }

  /**
   * Get message word count
   */
  getMessageWordCount(content: string): number {
    return content.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  /**
   * Get message character count
   */
  getMessageCharCount(content: string): number {
    return content.length;
  }

  /**
   * Validate message content
   */
  validateMessageContent(content: string): {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check if content is empty
    if (!content || content.trim().length === 0) {
      errors.push('Message content cannot be empty');
    }

    // Check content length
    if (content.length > 10000) {
      errors.push('Message content too long (max 10,000 characters)');
    }

    // Check for very long content
    if (content.length > 5000) {
      warnings.push('Message content is very long');
    }

    // Check word count
    const wordCount = this.getMessageWordCount(content);
    if (wordCount > 2000) {
      warnings.push('Message has many words, consider splitting');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}