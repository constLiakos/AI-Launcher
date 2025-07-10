import { app } from 'electron';
import { PrismaClient } from 'generated/client';
import { getDatabasePath, getAppDataPath } from '@main/utils/config';

import { exec } from 'child_process';
import { promisify } from 'util';
import { existsSync, mkdirSync } from 'fs';
import * as path from 'path';
import { promises as fs } from 'fs';

const execAsync = promisify(exec);

export class DatabaseService {
  private prisma: PrismaClient | null = null;
  private isInitialized = false;
  private databasePath: string;

  constructor() {
    this.databasePath = getDatabasePath();
  }
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      await this.ensureDatabaseDirectory();

      this.prisma = new PrismaClient({
        datasources: {
          db: {
            url: `file:${this.databasePath}`,
          },
        },
        log: process.env.NODE_ENV === 'development' ? ['warn', 'error'] : ['error'],
      });

      await this.prisma.$connect();

      await this.setupDatabase();

      this.isInitialized = true;
      console.log(`Database initialized successfully at: ${this.databasePath}`);

    } catch (error) {
      console.error('Failed to initialize database:', error);

      if (error instanceof Error) {
        throw new Error(`Database initialization failed: ${error.message}`);
      } else {
        throw new Error(`Database initialization failed with an unknown error: ${String(error)}`);
      }
    }
  }

  private async ensureDatabaseDirectory(): Promise<void> {
    const dbDir = getAppDataPath();
    if (!existsSync(dbDir)) {
      mkdirSync(dbDir, { recursive: true });
      console.log(`Created database directory: ${dbDir}`);
    }
  }

  /**
   * Runs `prisma db push` programmatically to sync the schema.
   */
  private async setupDatabase(): Promise<void> {
    if (!this.prisma) {
      throw new Error('Prisma client is not available for setup.');
    }

    try {
      // Checking if the main table 'Conversation' already exists.
      const conversationTable = await this.prisma.$queryRawUnsafe<Array<{ name: string }>>(
        `SELECT name FROM sqlite_master WHERE type='table' AND name='Conversation';`
      );
      // If the table exists, the database is already set up. We do nothing.

      if (conversationTable.length > 0) {
        console.log('Database schema already exists.');
        return;
      }
      // If it doesn't exist, then we create the schema from the file.

      console.log('Database schema not found. Creating from schema.sql...');

      const schemaSqlPath = app.isPackaged
        ? path.join(process.resourcesPath, 'resources/schema.sql')
        : path.join(app.getAppPath(), 'src/main/resources/schema.sql');

      const schemaSql = await fs.readFile(schemaSqlPath, 'utf-8');
      // Split the SQL into separate statements and remove empty ones.
      const sqlCommands = schemaSql
        .split(';')
        .map(cmd => cmd.trim())
        .filter(cmd => cmd.length > 0);
      // Execute all commands within a transaction for safety.

      await this.prisma.$transaction(
        sqlCommands.map(command => this.prisma!.$executeRawUnsafe(command))
      );

      console.log('Database schema created successfully.');

    } catch (error) {
      console.error('Failed to setup database schema:', error);
      throw error;
    }
  }

  /**
   * Get the Prisma client instance
   */
  getClient(): PrismaClient {
    if (!this.prisma) {
      throw new Error('Database not initialized. Call initialize() first.');
    }
    return this.prisma;
  }

  /**
   * Check if database is initialized
   */
  isReady(): boolean {
    return this.isInitialized && this.prisma !== null;
  }

  /**
   * Get database statistics
   */
  async getStats(): Promise<{
    conversationCount: number;
    messageCount: number;
    databaseSize: string;
    lastModified: Date | null;
  }> {
    if (!this.prisma) {
      throw new Error('Database not initialized');
    }

    try {
      const [conversationCount, messageCount] = await Promise.all([
        this.prisma.conversation.count(),
        this.prisma.message.count()
      ]);

      // Get database file stats
      let databaseSize = 'Unknown';
      let lastModified: Date | null = null;

      try {
        const { statSync } = await import('fs');
        const stats = statSync(this.databasePath);
        databaseSize = this.formatBytes(stats.size);
        lastModified = stats.mtime;
      } catch (error) {
        console.warn('Could not get database file stats:', error);
      }

      return {
        conversationCount,
        messageCount,
        databaseSize,
        lastModified
      };
    } catch (error) {
      console.error('Failed to get database stats:', error);
      throw error;
    }
  }

  /**
   * Optimize database (VACUUM and ANALYZE)
   */
  async optimize(): Promise<void> {
    if (!this.prisma) {
      throw new Error('Database not initialized');
    }

    try {
      console.log('Starting database optimization...');
      
      // Run VACUUM to reclaim space
      await this.prisma.$executeRaw`VACUUM`;
      console.log('Database VACUUM completed');

      // Run ANALYZE to update query planner statistics
      await this.prisma.$executeRaw`ANALYZE`;
      console.log('Database ANALYZE completed');

      console.log('Database optimization completed successfully');
    } catch (error) {
      console.error('Database optimization failed:', error);
      throw error;
    }
  }

  /**
   * Backup database to a file
   */
  async backup(backupPath: string): Promise<void> {
    try {
      const { copyFileSync } = await import('fs');
      
      // Ensure database is flushed
      if (this.prisma) {
        await this.prisma.$executeRaw`PRAGMA wal_checkpoint(FULL)`;
      }

      // Copy database file
      copyFileSync(this.databasePath, backupPath);
      console.log(`Database backed up to: ${backupPath}`);
    } catch (error) {
      console.error('Database backup failed:', error);
      throw error;
    }
  }

  /**
   * Restore database from a backup file
   */
  async restore(backupPath: string): Promise<void> {
    if (!existsSync(backupPath)) {
      throw new Error(`Backup file does not exist: ${backupPath}`);
    }

    try {
      // Disconnect current connection
      if (this.prisma) {
        await this.prisma.$disconnect();
        this.prisma = null;
      }

      // Copy backup file over current database
      const { copyFileSync } = await import('fs');
      copyFileSync(backupPath, this.databasePath);

      // Reinitialize database connection
      await this.initialize();
      
      console.log(`Database restored from: ${backupPath}`);
    } catch (error) {
      console.error('Database restore failed:', error);
      throw error;
    }
  }

  /**
   * Clear all data from database
   */
  async clearAllData(): Promise<void> {
    if (!this.prisma) {
      throw new Error('Database not initialized');
    }

    try {
      // Delete in correct order due to foreign key constraints
      await this.prisma.message.deleteMany();
      await this.prisma.conversation.deleteMany();
      
      console.log('All database data cleared');
    } catch (error) {
      console.error('Failed to clear database data:', error);
      throw error;
    }
  }

  /**
   * Execute a raw SQL query (use with caution)
   */
  async executeRaw(query: string, params: any[] = []): Promise<any> {
    if (!this.prisma) {
      throw new Error('Database not initialized');
    }

    try {
      return await this.prisma.$queryRawUnsafe(query, ...params);
    } catch (error) {
      console.error('Raw query execution failed:', error);
      throw error;
    }
  }

  /**
   * Begin a transaction
   */
  async transaction<T>(
    fn: (prisma: Omit<PrismaClient, '$connect' | '$disconnect' | '$on' | '$transaction' | '$use' | '$extends'>) => Promise<T>
  ): Promise<T> {
    if (!this.prisma) {
      throw new Error('Database not initialized');
    }

    return await this.prisma.$transaction(fn);
  }

  /**
   * Health check - verify database connectivity and integrity
   */
  async healthCheck(): Promise<{
  connected: boolean;
  tablesExist: boolean;
  canWrite: boolean;
  errors: string[];
}> {
  const result = {
    connected: false,
    tablesExist: false,
    canWrite: false,
    errors: [] as string[] // ← Type assertion
  };

  try {
    if (!this.prisma) {
      result.errors.push('Prisma client not initialized');
      return result;
    }

    // Test connection
    await this.prisma.$queryRaw`SELECT 1`;
    result.connected = true;

    // Check if tables exist
    const tables = await this.prisma.$queryRaw`
      SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Conversation', 'Message')
    ` as Array<{ name: string }>;
    
    result.tablesExist = tables.length === 2;
    if (!result.tablesExist) {
      result.errors.push('Required database tables do not exist');
    }

    // Test write capability
    const testId = `health-check-${Date.now()}`;
    await this.prisma.conversation.create({
      data: {
        id: testId,
        title: 'Health Check Test'
      }
    });
    
    await this.prisma.conversation.delete({
      where: { id: testId }
    });
    
    result.canWrite = true;

  } catch (error) {
    result.errors.push(`Health check failed: ${error}`);
  }

  return result;
}

  /**
   * Get database path
   */
  getDatabasePath(): string {
    return this.databasePath;
  }

  /**
   * Close database connection and cleanup
   */
  async cleanup(): Promise<void> {
    if (this.prisma) {
      try {
        await this.prisma.$disconnect();
        console.log('Database connection closed');
      } catch (error) {
        console.error('Error closing database connection:', error);
      } finally {
        this.prisma = null;
        this.isInitialized = false;
      }
    }
  }

  /**
   * Format bytes to human readable format
   */
  private formatBytes(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Destructor - ensure cleanup on process exit
   */
  async destroy(): Promise<void> {
    await this.cleanup();
  }
}