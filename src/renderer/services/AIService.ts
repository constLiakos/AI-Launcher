// src/renderer/services/AIService.ts

import { AIMessage } from '@shared/types';

export const AIService = {
  generateResponse: async (messages: AIMessage[]): Promise<string> => {
    if (window.electronAPI && window.electronAPI.generateAIResponse) {
      try {
        const response = await window.electronAPI.generateAIResponse(messages);
        return response;
      } catch (error) {
        console.error('Error calling AI service via IPC:', error);
        return 'Error: Could not get a response from the AI.';
      }
    }
    return 'Error: AI service is not available.';
  },
};