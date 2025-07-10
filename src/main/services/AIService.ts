// src/main/services/AIService.ts

import { MainConfigService } from '@main/services/ConfigService';
import { AIMessage, LLMProvider, LLMProviderType, Model } from '@shared/types';
import OpenAI from 'openai';
import { WebContents } from 'electron';

export class AIService {
  private configService: MainConfigService;

  constructor() {
    this.configService = MainConfigService.getInstance();
  }

  async generateResponse(messages: AIMessage[]): Promise<string> {
    const config = await this.configService.getConfig();
    const modelId = config.defaultChatModelId;
    if (!modelId) {
      throw new Error('No default chat model is configured in settings.');
    }
    const provider = config.providers.find(p =>
      (p.availableModels ?? []).some(m => m.id === modelId) ||
      (p.customModels ?? []).some(m => m.id === modelId)
    );
    if (!provider) {
      throw new Error(`The provider for the default model '${modelId}' could not be found. Please check your settings.`);
    }
    if (!provider.apiKey) {
      throw new Error(`API key for provider '${provider.name}' is not set.`);
    }
    const openai = new OpenAI({
      apiKey: provider.apiKey,
      baseURL: provider.apiBase,
    });
    try {
      const completion = await openai.chat.completions.create({
        model: modelId,
        messages: messages as any,
        temperature: provider.temperature,
        max_tokens: provider.maxTokens,
        stream: false,
      });

      return completion.choices[0]?.message?.content || 'No response from AI.';
    } catch (error) {
      console.error('Error calling OpenAI API:', error);
      throw new Error(`AI request failed for model ${modelId}: ${(error as Error).message}`);
    }
  }

  public async generateResponseStream(
    payload: { messages: AIMessage[], tempMessageId: string, modelId: string, providerId: string },
    sender: WebContents
  ): Promise<void> {
    const { messages, tempMessageId, modelId, providerId } = payload;
    const config = await this.configService.getConfig();
    
    const provider = config.providers.find(p => p.id === providerId);

    if (!provider) {
      const errorMsg = `Provider with ID: ${providerId} not found.`;
      console.error(errorMsg);
      sender.send('ai:stream-chunk', { tempMessageId, error: errorMsg, isFinal: true });
      return;
    }

    const openai = new OpenAI({
      apiKey: provider.apiKey,
      baseURL: provider.apiBase,
    });

    try {
      const stream = await openai.chat.completions.create({
        model: modelId,
        messages: messages as any,
        stream: true,
      });

      let fullContent = '';
      for await (const chunk of stream) {
        const token = chunk.choices[0]?.delta?.content || '';
        if (token) {
          fullContent += token;
          sender.send('ai:stream-chunk', {
            tempMessageId,
            content: token,
            isFinal: false,
          });
        }
      }
      
      sender.send('ai:stream-chunk', {
        tempMessageId,
        content: fullContent,
        isFinal: true,
      });

    } catch (error) {
      console.error('AI Stream Error:', error);
      sender.send('ai:stream-chunk', { tempMessageId, error: (error as Error).message, isFinal: true });
    }
  }

  /**
   * Fetches available models from a given provider.
   * @param provider The LLM provider configuration.
   * @returns A promise that resolves to an array of Model objects.
   */
  async fetchAvailableModels(provider: LLMProvider): Promise<Model[]> {
    if (!provider.apiKey) {
      console.warn(`API key for provider ${provider.name} is not set. Skipping model fetch.`);
      return [];
    }

    try {
      switch (provider.type) {
        case LLMProviderType.OPENAI:
        case LLMProviderType.GROQ:
        case LLMProviderType.TOGETHER:
        case LLMProviderType.FIREWORKS:
          return this.fetchOpenAICompatibleModels(provider);
        
        case LLMProviderType.OLLAMA:
          return this.fetchOllamaModels(provider);

        default:
          console.warn(`Model fetching not implemented for provider type: ${provider.type}`);
          return [];
      }
    } catch (error) {
      console.error(`Failed to fetch models for provider ${provider.name}:`, error);
      return [];
    }
  }

  /**
   * Fetches models from an OpenAI-compatible API endpoint.
   */
  private async fetchOpenAICompatibleModels(provider: LLMProvider): Promise<Model[]> {
    const url = `${provider.apiBase.replace(/\/$/, '')}/models`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${provider.apiKey}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}: ${await response.text()}`);
    }

    const jsonResponse = await response.json() as { data: { id: string }[] };
    
    return jsonResponse.data.map(model => ({
      id: model.id,
      name: model.id,
      providerType: provider.type,
      providerId: provider.id,
    }));
  }

  /**
   * Fetches models from an Ollama API endpoint.
   */
  private async fetchOllamaModels(provider: LLMProvider): Promise<Model[]> {
    const url = `${provider.apiBase.replace(/\/$/, '')}/api/tags`;
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}: ${await response.text()}`);
    }

    const jsonResponse = await response.json() as { models: { name: string }[] };

    return jsonResponse.models.map(model => ({
      id: model.name,
      name: model.name,
      providerType: provider.type,
      providerId: provider.id,
    }));
  }
}