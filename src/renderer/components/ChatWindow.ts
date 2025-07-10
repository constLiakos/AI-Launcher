// src/renderer/components/ChatWindow.ts
import { v4 as uuidv4 } from 'uuid';
import { getWindowSize } from '@shared/constants/window';
import { WindowState, InputMode, RecordingState, Message, MessageRole, Attachment, AIMessage } from '@shared/types';
import { InputArea, InputAreaCallbacks } from '@renderer/components/InputArea';
import { ConversationArea } from '@renderer/components/ConversationArea';
import { ConversationList, ConversationListCallbacks } from '@renderer/components/ConversationList';
import { ConversationManager } from '@renderer/managers/ConversationManager';
import { SttService } from '@renderer/services/SttService';
import { NotificationService } from '@renderer/services/NotificationService'; 

export class ChatWindow {
  private element: HTMLElement;
  private mainContentElement: HTMLElement;
  private inputArea: InputArea;
  private conversationArea: ConversationArea;
  private conversationList: ConversationList;
  private conversationManager: ConversationManager;
  private isHistoryVisible = false;

  private windowState: WindowState = WindowState.COMPACT;
  private recordingState: RecordingState = RecordingState.IDLE;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor(container: HTMLElement) {
    this.element = this.createWindowElement();
    this.mainContentElement = this.createMainContentElement();
    this.conversationManager = ConversationManager.getInstance();

    const inputAreaCallbacks: InputAreaCallbacks = {
      onSendMessage: this.handleSendMessage.bind(this),
      onToggleRecording: this.handleToggleRecording.bind(this),
      onOpenSettings: this.handleOpenSettings.bind(this),
      onToggleHistory: this.toggleHistorySidebar.bind(this),
      onToggleConversation: this.toggleConversationArea.bind(this),
      onInputModeChange: this.handleInputModeChange.bind(this),
      onInputWindowResize: this.handleInputWindowResize.bind(this),
    };

    const conversationListCallbacks: ConversationListCallbacks = {
      onConversationSelect: this.handleConversationSelect.bind(this),
      onConversationDelete: this.handleConversationDelete.bind(this),
      onNewConversation: this.handleNewConversation.bind(this),
      onClearAll: this.handleClearAllConversations.bind(this),
      onCloseList: this.hideHistorySidebar.bind(this),
    };
    
    this.inputArea = new InputArea(inputAreaCallbacks);
    this.conversationArea = new ConversationArea();
    this.conversationList = new ConversationList(conversationListCallbacks);
    
    this.element.appendChild(this.conversationList.getElement());
    this.mainContentElement.appendChild(this.inputArea.getElement());
    this.mainContentElement.appendChild(this.conversationArea.getElement());
    this.element.appendChild(this.mainContentElement);
    
    container.appendChild(this.element);
    container.appendChild(this.createConfirmationContainer())
    
    const notificationContainer = document.getElementById('notification-container');
    if (notificationContainer) {
      NotificationService.init(notificationContainer);
    }
    
    
    this.bindConversationAreaEvents();
    this.updateWindowState();
    this.inputArea.focus();
    this.initializeConversation();
  }
  
  private async initializeConversation(): Promise<void> {
    const conversation = await this.conversationManager.loadOrCreateConversation();
    this.conversationArea.loadConversation(conversation);
    this.conversationList.setActiveConversation(conversation.id);
    await this.refreshConversationList();
  }

  private async toggleHistorySidebar(): Promise<void> {
    this.isHistoryVisible = this.conversationList.toggle();
    if (this.isHistoryVisible){
      this.setWindowState(WindowState.EXPANDED);
      this.conversationArea.show()
      this.inputArea.setExpanded(true);
    }
    this.updateWindowState();

    if(this.isHistoryVisible) {
      await this.refreshConversationList();
    }
  }

  private async hideHistorySidebar(): Promise<void> {
    this.conversationList.hide()
    this.isHistoryVisible = false;
    this.updateWindowState();
  }

  private async refreshConversationList(): Promise<void> {
    const allConversations = await this.conversationManager.getAllConversations();
    this.conversationList.render(allConversations);
  }

  private async handleConversationSelect(conversationId: string): Promise<void> {
    console.log(`Switching to conversation: ${conversationId}`);
    const conversation = await this.conversationManager.loadAndSetActiveConversation(conversationId);
    console.log("handleConversationSelect");
    console.log(conversation);
    if(conversation) {
        this.conversationArea.loadConversation(conversation);
        this.conversationList.setActiveConversation(conversationId);
    }
    else{
      const error = `Conversation does not exist`;
      console.log(error);
      NotificationService.showError(error);
    }
  }

  private async handleConversationDelete(conversationId: string): Promise<void> {
    const msg = `Deleting conversation: ${conversationId}`;
    console.log(msg);
    await this.conversationManager.deleteConversation(conversationId);
    await this.refreshConversationList();
    const activeConv = this.conversationManager.getActiveConversation();
    if (!activeConv || activeConv.id === conversationId) {
      const newConv = await this.conversationManager.loadOrCreateConversation();
      this.conversationArea.loadConversation(newConv);
      this.conversationList.setActiveConversation(newConv.id);
    }
    NotificationService.showSuccess("Deleted!");
  }

  private async handleClearAllConversations(): Promise<void> {
    console.log('Clearing all conversations...');
    await this.conversationManager.clearAllConversations();
    await this.refreshConversationList();
    const newConv = this.conversationManager.getActiveConversation();
    if (newConv) {
        this.conversationArea.loadConversation(newConv);
        this.conversationList.setActiveConversation(newConv.id);
    }
    NotificationService.showSuccess("Cleared!");
  }

  private async handleNewConversation(): Promise<void> {
      console.log('Creating new conversation from sidebar...');
      const newConv = this.conversationManager.createNewConversation();
      this.conversationArea.loadConversation(newConv);
      this.conversationList.setActiveConversation(newConv.id);
      await this.refreshConversationList();
  }
  
  private createWindowElement(): HTMLElement {
    const div = document.createElement('div');
    div.className = 'chat-window window-compact';
    div.id = 'chat-window-container';
    return div;
  }

  private createConfirmationContainer(): HTMLElement{
    const div = document.createElement('div');
    div.id = 'notification-container'
    div.className = 'notification-container'
    return div;
  }

  private createMainContentElement(): HTMLElement {
    const div = document.createElement('div');
    div.className = 'main-content';
    return div;
  }

  private bindConversationAreaEvents(): void {
    this.conversationArea.onClear(this.clearConversation.bind(this));
    this.conversationArea.onNew(this.newConversation.bind(this));
  }

  private async handleSendMessage(payload: { text: string; attachments: Attachment[] }): Promise<void> {
      this.conversationArea.resetScrollState();
      const { text, attachments } = payload;
      if (!text.trim() && attachments.length === 0) return;

      const userMessage = await this.conversationManager.addMessage(text, MessageRole.USER, attachments);
      this.addMessageToUI(userMessage);
      
      const tempMessageId = `temp_${uuidv4()}`;
      const assistantMessagePlaceholder: Message = {
          id: tempMessageId,
          role: MessageRole.ASSISTANT,
          content: '▋',
          createdAt: new Date(),
          conversationId: this.conversationManager.getActiveConversation()!.id,
      };
      this.addMessageToUI(assistantMessagePlaceholder);

      const messagesForAI = this._prepareMessagesForAI(this.conversationManager.getActiveMessages());

      let fullResponse = '';
      const unsubscribe = window.electronAPI.onAIStreamChunk(async (chunk) => {
          if (chunk.tempMessageId !== tempMessageId) return;

          if (chunk.error) {
              const error = `Error: ${chunk.error}`;
              this.conversationArea.updateMessageError(tempMessageId, error);
              NotificationService.showError(error);
              await this.conversationManager.finalizeAssistantMessage(tempMessageId, "unknown_error", chunk.error);
              unsubscribe();
              return;
          }
        
          if (chunk.isFinal) {
              unsubscribe();
              await this.conversationManager.finalizeAssistantMessage(tempMessageId, chunk.content!);
          } else {
              fullResponse += chunk.content;
              this.conversationArea.updateMessageContent(tempMessageId, fullResponse);

              this.attachThinkToggleListeners();
          }
      });

      const config = await window.electronAPI.loadConfig();
      const modelId = config.defaultChatModelId;
      if (!modelId) {
          const error = "No default chat model is set."
          console.error(error);
          NotificationService.showError(error)
          this.conversationArea.updateMessageError(tempMessageId, error);
          await this.conversationManager.finalizeAssistantMessage(tempMessageId, "no_chat_model", error);

          return;
      }
      const provider = config.providers.find(p =>
          (p.availableModels || []).some(m => m.id === modelId) ||
          (p.customModels || []).some(m => m.id === modelId)
      );
      
      if (!provider) {
          const error = `Could not find a provider for the default model ID: ${modelId}`
          console.error(error);
          NotificationService.showError(error);
          return;
      }

      window.electronAPI.generateAIStream({
          messages: messagesForAI,
          tempMessageId,
          modelId: modelId,
          providerId: provider.id
      });
      
      this.inputArea.clearInput();
  }

  private attachThinkToggleListeners(): void {
      const buttons = this.conversationArea.getElement().querySelectorAll('.think-toggle-btn');
      const lastButton = buttons[buttons.length - 1];
      if (lastButton) {
          lastButton.addEventListener('click', (event) => {
              const thinkContent = (event.target as HTMLElement).closest('.think-container');
              if (thinkContent) {
                  thinkContent.classList.toggle('collapsed');
              }
          });
      }
  }

  /**
   * Converts the application's messages into a format understood by the AI service,
   * supporting multimodal content (text + images).
   */
  private _prepareMessagesForAI(messages: Message[]): AIMessage[] {
    return messages.map(msg => {
      // Handling user messages with attachments
      if (msg.role === MessageRole.USER && msg.attachments && msg.attachments.length > 0) {
        
        let combinedContent = msg.content || '';
        const imageContentParts: { type: 'image_url'; image_url: { url: string } }[] = [];

        msg.attachments.forEach(att => {
          if (att.type === 'image' || att.type === 'screen-capture') {
            imageContentParts.push({
              type: 'image_url',
              image_url: { url: att.data }
            });
          } else if (att.type === 'pdf' && att.extractedText) {
            combinedContent += `\n\n--- Content from ${att.filename} ---\n${att.extractedText}`;
          }
        });

        const contentParts: any[] = [{ type: 'text', text: combinedContent.trim() }];
        
        return { 
          role: msg.role, 
          content: contentParts.concat(imageContentParts) 
        };
      }
      // For messages without attachments or for assistant messages
      
      return { role: msg.role, content: msg.content };
    });
  }


  private handleToggleRecording(): void {
    switch (this.recordingState) {
      case RecordingState.IDLE:
        this.startRecording();
        break;
      case RecordingState.RECORDING:
        this.stopRecording();
        break;
      case RecordingState.PROCESSING:
        // Do nothing, waiting for processing to finish
        break;
    }
  }

  private handleOpenSettings(): void {
    window.electronAPI?.onSettingsOpen();
  }

  private handleInputModeChange(mode: InputMode): void {
    this.updateWindowState();
  }

  private handleInputWindowResize() : void {
    if (!this.inputArea) return;
    const input_area_heights = this.inputArea.getInputAreaHeight();
    let baseState = this.conversationArea.isElementVisible() ? WindowState.EXPANDED : WindowState.COMPACT;
    
    const dimensions = getWindowSize(baseState, input_area_heights.input_area, this.isHistoryVisible);
    this.resizeWindow(null, dimensions.height);

    if (this.inputArea){
      this.inputArea.setInputFieldHeight(input_area_heights.input_field)
    }
  }

  private toggleConversationArea(): void {
    const isVisible = this.conversationArea.toggle();
    this.setWindowState(isVisible ? WindowState.EXPANDED : WindowState.COMPACT, true);
    this.inputArea.setExpanded(isVisible);
    if(!isVisible){
      this.hideHistorySidebar();
    }
  }

  private setWindowState(state: WindowState, ignoreWidthChange:boolean=false): void {
    this.windowState = state;
    this.updateWindowState(ignoreWidthChange);
  }

  private updateWindowState(ignoreWidthChange:boolean=false): void {
    let baseState = this.conversationArea.isElementVisible() ? WindowState.EXPANDED : WindowState.COMPACT;
    this.element.className = `chat-window window-${baseState}`;
    const input_area_heights = this.inputArea.getInputAreaHeight();
    const dimensions = getWindowSize(baseState, input_area_heights.input_area, this.isHistoryVisible);
    this.resizeWindow(ignoreWidthChange ? null : dimensions.width, dimensions.height);
  }

  private addMessageToUI(message: Message): void {
    this.conversationArea.addMessage(message);
    if (this.windowState === WindowState.COMPACT) {
      this.toggleConversationArea();
    }
  }
  
  private async newConversation(): Promise<void> {
    await this.handleNewConversation();
  }

  private async clearConversation(): Promise<void> {
    const activeConv = this.conversationManager.getActiveConversation();
    if (activeConv) {
      await window.electronAPI.clearMessagesByConversation(activeConv.id);
      const reloadedConv = await this.conversationManager.loadOrCreateConversation(activeConv.id);
      this.conversationArea.loadConversation(reloadedConv);
    }
  }

  private resizeWindow(width: number|null, height: number|null): void {
    window.electronAPI?.resizeWindow(width, height);
  }

  public focusInput(): void {
    this.inputArea.focus();
  }

  private async startRecording(): Promise<void> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };

      this.mediaRecorder.onstop = () => this.handleRecordingStop();

      this.mediaRecorder.start();
      this.recordingState = RecordingState.RECORDING;
      this.inputArea.setRecordingState(this.recordingState);

    } catch (error) {
      console.error('Error starting recording:', error);
      const error_msg = 'Could not start recording. Please ensure microphone permissions are granted';
      NotificationService.showError(error_msg);
      
      
      this.recordingState = RecordingState.IDLE;
      this.inputArea.setRecordingState(this.recordingState);
    }
  }

  private stopRecording(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }
  }

  private async handleRecordingStop(): Promise<void> {
    if (this.audioChunks.length === 0) {
      console.warn('No audio data recorded.');
      this.recordingState = RecordingState.IDLE;
      this.inputArea.setRecordingState(this.recordingState);
      return;
    }
    
    this.recordingState = RecordingState.PROCESSING;
    this.inputArea.setRecordingState(this.recordingState);
    
    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
    
    try {
      const transcript = await SttService.transcribe(audioBlob);
      if (transcript) {
        const currentValue = this.inputArea.getValue();
        this.inputArea.setValue(currentValue ? `${currentValue.trim()} ${transcript}` : transcript);
        this.inputArea.focus();
      }
    } catch (error) {
      console.error('Transcription failed:', error);
      const error_msg = 'Failed to transcribe audio. Please check settings and connection.';
      NotificationService.showError(error_msg);
    } finally {
      this.audioChunks = [];
      this.mediaRecorder?.stream.getTracks().forEach(track => track.stop());
      this.mediaRecorder = null;
      this.recordingState = RecordingState.IDLE;
      this.inputArea.setRecordingState(this.recordingState);
    }
  }


}