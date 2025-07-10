// src/main/services/AttachmentService.ts

import pdfParse from 'pdf-parse';
import { AppConfig } from '@shared/config/AppConfig';

// TODO add convertToImage
export type PdfProcessingStrategy = 'extractText';

export class AttachmentService {
  private static instance: AttachmentService;
  private config: AppConfig;

  private constructor(config: AppConfig) {
    this.config = config;
  }

  public static getInstance(config: AppConfig): AttachmentService {
    if (!AttachmentService.instance) {
      AttachmentService.instance = new AttachmentService(config);
    }
    return AttachmentService.instance;
  }

    /**
   * Processes a PDF attachment based on the strategy defined in the settings.
   * @param dataUrl The PDF as a base64 Data URL.
   * @returns The extracted text or a string indicating other processing.
   */
  public async processPdf(dataUrl: string): Promise<{ extractedText: string | null }> {
    const strategy: PdfProcessingStrategy = this.config.conversation.pdfProcessingStrategy || 'extractText';

    switch (strategy) {
      case 'extractText':
        return this.extractTextFromPdf(dataUrl);
      // case 'convertToImage':
      //   return Promise.resolve({ extractedText: null }); 
      default:
        console.warn(`Unknown PDF processing strategy: ${strategy}`);
        return Promise.resolve({ extractedText: null });
    }
  }

  /**
   * Converts a base64 Data URL to a Buffer and extracts its text.
   */
  private async extractTextFromPdf(dataUrl: string): Promise<{ extractedText: string }> {
    try {
      if (!dataUrl.startsWith('data:application/pdf;base64,')) {
        throw new Error('Invalid PDF Data URL format.');
      }

      // Extracting the base64 data
      const base64Data = dataUrl.substring('data:application/pdf;base64,'.length);
      const buffer = Buffer.from(base64Data, 'base64');

      const data = await pdfParse(buffer);
      
      return { extractedText: data.text };

    } catch (error) {
      console.error('Failed to parse PDF for text extraction:', error);
      throw new Error('Could not read text from the PDF file.');
    }
  }
}