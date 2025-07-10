// src/main/services/SttService.ts

import { MainConfigService } from '@main/services/ConfigService';
import OpenAI from 'openai';
import { promises as fs } from 'fs';
import * as os from 'os';
import * as path from 'path';

export class SttService {
  private configService: MainConfigService;

  constructor() {
    this.configService = MainConfigService.getInstance();
  }

  async transcribe(audioBuffer: Buffer): Promise<string> {
    const config = await this.configService.getConfig();
    const sttSettings = config.stt;

    if (!sttSettings || !sttSettings.enabled) {
      throw new Error('STT service is not enabled in settings.');
    }

    if (!sttSettings.apiKey) {
      throw new Error('API key for the STT provider is not set.');
    }

    const openai = new OpenAI({
      apiKey: sttSettings.apiKey,
      baseURL: sttSettings.apiBase,
    });

    // Create a temporary file path
    const tempFilePath = path.join(os.tmpdir(), `audio-${Date.now()}.webm`);
    
    try {
      // Write the buffer to the temporary file
      await fs.writeFile(tempFilePath, audioBuffer);

      // Create a read stream from the temporary file
      const fileStream = require('fs').createReadStream(tempFilePath);
      
      const transcription = await openai.audio.transcriptions.create({
        file: fileStream,
        model: sttSettings.model,
      });

      return transcription.text;
    } catch (error) {
      console.error('Error calling STT API:', error);
      // Ensure we re-throw so the IPC handler can catch it
      throw new Error(`STT request failed: ${(error as Error).message}`);
    } finally {
      // Clean up the temporary file
      try {
        await fs.unlink(tempFilePath);
      } catch (cleanupError) {
        console.error('Failed to delete temporary audio file:', cleanupError);
      }
    }
  }
}