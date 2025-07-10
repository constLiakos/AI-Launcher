import { DatabaseService } from '@main/services/DatabaseService';
import { PrismaClient } from 'generated/client';
import { Attachment, Conversation, Message, stringToMessageRole } from '@shared/database-types'

type PrismaConversationWithMessages = import('@prisma/client').Conversation & {
    messages: import('@prisma/client').Message[];
};

export class ConversationService {
  private db: PrismaClient;

  constructor(private databaseService: DatabaseService) {
    this.db = this.databaseService.getClient();
  }

  /**
   * Create a new conversation
   */
  async createConversation(title: string): Promise<Conversation> {
    try {
      const conversation = await this.db.conversation.create({
        data: {
          title: title.trim() || 'New Conversation',
          createdAt: new Date(),
          updatedAt: new Date(),
          isArchived: false
        },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        }
      });

      console.log(`Created conversation: ${conversation.id} - ${conversation.title}`);
      return this.mapConversation(conversation as PrismaConversationWithMessages);
    } catch (error) {
      console.error('Failed to create conversation:', error);
      throw new Error(`Failed to create conversation: ${error}`);
    }
  }

  /**
   * Get all conversations
   */
  async getAllConversations(): Promise<Conversation[]> {
    try {
      const conversations = await this.db.conversation.findMany({
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        },
        orderBy: {
          updatedAt: 'desc'
        }
      });

      return conversations.map((conv): Conversation => this.mapConversation(conv as PrismaConversationWithMessages));
    } catch (error) {
      console.error('Failed to get all conversations:', error);
      throw new Error(`Failed to get conversations: ${error}`);
    }
  }


  /**
   * Get conversations with pagination
   */
  async getConversationsPaginated(
    page: number = 1, 
    limit: number = 20
  ): Promise<{
    conversations: Conversation[];
    total: number;
    page: number;
    pages: number;
  }> {
    try {
      const skip = (page - 1) * limit;
      
      const [conversations, total] = await Promise.all([
        this.db.conversation.findMany({
          include: {
            messages: {
              orderBy: {
                createdAt: 'asc'
              }
            }
          },
          orderBy: {
            updatedAt: 'desc'
          },
          skip,
          take: limit
        }),
        this.db.conversation.count()
      ]);

      return {
        conversations: conversations.map((conv): Conversation => this.mapConversation(conv as PrismaConversationWithMessages)),
        total,
        page,
        pages: Math.ceil(total / limit)
      };
    } catch (error) {
      console.error('Failed to get paginated conversations:', error);
      throw new Error(`Failed to get paginated conversations: ${error}`);
    }
  }

  /**
   * Get conversation by ID
   */
  async getConversationById(id: string): Promise<Conversation | null> {
    try {
      const conversation = await this.db.conversation.findUnique({
        where: { id },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        }
      });

      if (!conversation) {
        return null;
      }
      console.log(conversation)

      return this.mapConversation(conversation as PrismaConversationWithMessages);
    } catch (error) {
      console.error('Failed to get conversation by ID:', error);
      throw new Error(`Failed to get conversation: ${error}`);
    }
  }



  /**
   * Update conversation
   */
  async updateConversation(
    id: string, 
    data: { title?: string }
  ): Promise<Conversation> {
    try {
      const conversation = await this.db.conversation.update({
        where: { id },
        data: {
          ...data,
          updatedAt: new Date()
        },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        }
      });

      console.log(`Updated conversation: ${conversation.id} - ${conversation.title}`);
      return this.mapConversation(conversation as PrismaConversationWithMessages);
    } catch (error) {
      console.error('Failed to update conversation:', error);
      throw new Error(`Failed to update conversation: ${error}`);
    }
  }

  /**
   * Delete conversation
   */
  async deleteConversation(id: string): Promise<void> {
    try {
      await this.db.conversation.delete({
        where: { id }
      });

      console.log(`Deleted conversation: ${id}`);
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw new Error(`Failed to delete conversation: ${error}`);
    }
  }


  /**
   * Delete multiple conversations
   */
  async deleteConversations(ids: string[]): Promise<number> {
    try {
      const result = await this.db.conversation.deleteMany({
        where: {
          id: {
            in: ids
          }
        }
      });

      console.log(`Deleted ${result.count} conversations`);
      return result.count;
    } catch (error) {
      console.error('Failed to delete conversations:', error);
      throw new Error(`Failed to delete conversations: ${error}`);
    }
  }

  /**
   * Clear all conversations
   */
  async clearAllConversations(): Promise<void> {
    try {
      await this.db.message.deleteMany();
      const result = await this.db.conversation.deleteMany();
      console.log(`Cleared all conversations (${result.count} deleted)`);
    } catch (error) {
      console.error('Failed to clear all conversations:', error);
      throw new Error(`Failed to clear conversations: ${error}`);
    }
  }



  /**
   * Search conversations by title
   */
  async searchConversations(query: string): Promise<Conversation[]> {
    try {
      const conversations = await this.db.conversation.findMany({
        where: {
          title: {
            contains: query
          }
        },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        },
        orderBy: {
          updatedAt: 'desc'
        }
      });

      return conversations.map((conv): Conversation => this.mapConversation(conv as PrismaConversationWithMessages));
    } catch (error) {
      console.error('Failed to search conversations:', error);
      throw new Error(`Failed to search conversations: ${error}`);
    }
  }
  /**
   * Get conversation statistics
   */
  async getConversationStats(): Promise<{
    totalConversations: number;
    totalMessages: number;
    averageMessagesPerConversation: number;
    oldestConversation: Date | null;
    newestConversation: Date | null;
  }> {
    try {
      const [
        totalConversations,
        totalMessages,
        oldestConv,
        newestConv
      ] = await Promise.all([
        this.db.conversation.count(),
        this.db.message.count(),
        this.db.conversation.findFirst({
          orderBy: { createdAt: 'asc' },
          select: { createdAt: true }
        }),
        this.db.conversation.findFirst({
          orderBy: { createdAt: 'desc' },
          select: { createdAt: true }
        })
      ]);

      return {
        totalConversations,
        totalMessages,
        averageMessagesPerConversation: totalConversations > 0 
          ? Math.round(totalMessages / totalConversations * 100) / 100 
          : 0,
        oldestConversation: oldestConv?.createdAt || null,
        newestConversation: newestConv?.createdAt || null
      };
    } catch (error) {
      console.error('Failed to get conversation stats:', error);
      throw new Error(`Failed to get conversation stats: ${error}`);
    }
  }

  /**
   * Get recent conversations
   */
  async getRecentConversations(limit: number = 10): Promise<Conversation[]> {
    try {
      const conversations = await this.db.conversation.findMany({
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        },
        orderBy: {
          updatedAt: 'desc'
        },
        take: limit
      });

      return conversations.map((conv): Conversation => this.mapConversation(conv as PrismaConversationWithMessages));
    } catch (error) {
      console.error('Failed to get recent conversations:', error);
      throw new Error(`Failed to get recent conversations: ${error}`);
    }
  }


  /**
   * Duplicate conversation
   */
  async duplicateConversation(id: string, newTitle?: string): Promise<Conversation> {
    try {
      const originalConv = await this.getConversationById(id);
      if (!originalConv) {
        throw new Error('Original conversation not found');
      }

      const duplicatedConv = await this.createConversation(
        newTitle || `Copy of ${originalConv.title}`
      );

      // Copy messages if any
      if (originalConv.messages && originalConv.messages.length > 0) {
        for (const message of originalConv.messages) {
          await this.db.message.create({
            data: {
              content: message.content,
              role: message.role,
              conversationId: duplicatedConv.id,
              createdAt: new Date()
            }
          });
        }
      }

      return await this.getConversationById(duplicatedConv.id) as Conversation;
    } catch (error) {
      console.error('Failed to duplicate conversation:', error);
      throw new Error(`Failed to duplicate conversation: ${error}`);
    }
  }

  /**
   * Update conversation timestamp (mark as recently used)
   */
  async touchConversation(id: string): Promise<void> {
    try {
      await this.db.conversation.update({
        where: { id },
        data: {
          updatedAt: new Date()
        }
      });
    } catch (error) {
      console.error('Failed to touch conversation:', error);
    }
  }

  /**
   * Get conversation title by ID
   */
  private async getConversationTitle(id: string): Promise<string> {
    try {
      const conv = await this.db.conversation.findUnique({
        where: { id },
        select: { title: true }
      });
      return conv?.title || 'Unknown';
    } catch {
      return 'Unknown';
    }
  }



  /**
   * Check if conversation exists
   */
  async conversationExists(id: string): Promise<boolean> {
    try {
      const count = await this.db.conversation.count({
        where: { id }
      });
      return count > 0;
    } catch (error) {
      console.error('Failed to check conversation existence:', error);
      return false;
    }
  }

  /**
   * Export conversation to JSON
   */
  async exportConversation(id: string): Promise<string> {
    try {
      const conversation = await this.getConversationById(id);
      if (!conversation) {
        throw new Error('Conversation not found');
      }

      return JSON.stringify(conversation, null, 2);
    } catch (error) {
      console.error('Failed to export conversation:', error);
      throw new Error(`Failed to export conversation: ${error}`);
    }
  }

  /**
   * Import conversation from JSON
   */
  async importConversation(jsonData: string): Promise<Conversation> {
    try {
      const data = JSON.parse(jsonData);
      
      // Create new conversation
      const conversation = await this.createConversation(data.title || 'Imported Conversation');
      
      // Import messages if any
      if (data.messages && Array.isArray(data.messages)) {
        for (const messageData of data.messages) {
          await this.db.message.create({
            data: {
              content: messageData.content,
              role: messageData.role,
              conversationId: conversation.id,
              createdAt: new Date(),
            }
          });
        }
      }

      return await this.getConversationById(conversation.id) as Conversation;
    } catch (error) {
      console.error('Failed to import conversation:', error);
      throw new Error(`Failed to import conversation: ${error}`);
    }
  }

  async archiveConversation(id: string): Promise<Conversation> {
    try {
      const conversation = await this.db.conversation.update({
        where: { id },
        data: {
          isArchived: true,
          updatedAt: new Date()
        },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        }
      });

      console.log(`Archived conversation: ${conversation.id}`);
      return this.mapConversation(conversation as PrismaConversationWithMessages);
    } catch (error) {
      console.error('Failed to archive conversation:', error);
      throw new Error(`Failed to archive conversation: ${error}`);
    }
  }

  // Add unarchive method
  async unarchiveConversation(id: string): Promise<Conversation> {
    try {
      const conversation = await this.db.conversation.update({
        where: { id },
        data: {
          isArchived: false,
          updatedAt: new Date()
        },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        }
      });

      console.log(`Unarchived conversation: ${conversation.id}`);
      return this.mapConversation(conversation as PrismaConversationWithMessages);
    } catch (error) {
      console.error('Failed to unarchive conversation:', error);
      throw new Error(`Failed to unarchive conversation: ${error}`);
    }

  }

  // Add method to get archived conversations
  async getArchivedConversations(): Promise<Conversation[]> {
    try {
      const conversations = await this.db.conversation.findMany({
        where: {
          isArchived: true
        },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        },
        orderBy: {
          updatedAt: 'desc'
        }
      });

      return conversations.map((conv): Conversation => this.mapConversation(conv as PrismaConversationWithMessages));
    } catch (error) {
      console.error('Failed to get archived conversations:', error);
      throw new Error(`Failed to get archived conversations: ${error}`);
    }
  }

  async getActiveConversations(): Promise<Conversation[]> {
    try {
      const conversations = await this.db.conversation.findMany({
        where: {
          isArchived: false
        },
        include: {
          messages: {
            orderBy: {
              createdAt: 'asc'
            }
          }
        },
        orderBy: {
          updatedAt: 'desc'
        }
      });

      return conversations.map((conv): Conversation => this.mapConversation(conv as PrismaConversationWithMessages));
    } catch (error) {
      console.error('Failed to get active conversations:', error);
      throw new Error(`Failed to get active conversations: ${error}`);
    }
  }

  /**
   * Map database conversation to application type
   */
  private mapConversation(dbConversation: PrismaConversationWithMessages): Conversation {
    return {
      id: dbConversation.id,
      title: dbConversation.title,
      createdAt: dbConversation.createdAt,
      updatedAt: dbConversation.updatedAt,
      isArchived: dbConversation.isArchived,
      messages: dbConversation.messages?.map((msg): Message => ({
        id: msg.id,
        content: msg.content,
        attachments: msg.attachments ? (msg.attachments as unknown as Attachment[]) : [],
        error: msg.error ? msg.error : undefined,
        role: stringToMessageRole(msg.role),
        conversationId: msg.conversationId,
        createdAt: msg.createdAt
      })) || []
    };
  }
}