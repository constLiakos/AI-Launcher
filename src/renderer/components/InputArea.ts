import '../styles/components/input-area.css';
import { Attachment, InputMode, RecordingState, ScreenSource } from '@shared/types';
import { TEXT, WINDOW_SIZE } from '@shared/constants/index';
import { AttachmentMenu } from '@renderer/components/AttachmentMenu';
import { ScreenSourcePicker } from '@renderer/components/ScreenSourcePicker';
import { NotificationService } from '@renderer/services/NotificationService';

export interface InputAreaCallbacks {
  onSendMessage?: (payload: { text: string; attachments: Attachment[] }) => void;
  onToggleRecording?: () => void;
  onOpenSettings?: () => void;
  onToggleHistory?: () => void;
  onToggleConversation?: () => void;
  onInputModeChange?: (mode: InputMode) => void;
  onInputWindowResize?: () => void;
}

export class InputArea {
  private element: HTMLElement;
  private inputField: HTMLTextAreaElement;
  private attachButton: HTMLButtonElement;
  private fileInput: HTMLInputElement;
  private thumbnailsContainer: HTMLElement;
  private toggleButton: HTMLButtonElement;
  private recordButton: HTMLButtonElement;
  private settingsButton: HTMLButtonElement;
  private historyButton: HTMLButtonElement;
  private expandButton: HTMLButtonElement;
  private clearInputButton: HTMLButtonElement;
  private sendButton: HTMLButtonElement;
  private charCounter: HTMLElement;
  private attachmentMenu: AttachmentMenu;
  private screenSourcePicker: ScreenSourcePicker;
  private inputMode: InputMode = InputMode.SINGLE_LINE;
  private recordingState: RecordingState = RecordingState.IDLE;
  private isExpanded = false;
  private attachments: Attachment[] = [];
  private callbacks: InputAreaCallbacks = {};

  constructor(callbacks: InputAreaCallbacks = {}) {
    this.callbacks = callbacks;
    this.element = this.createElement();
    this.initializeElements();
    this.loadSttConfig();
    this.attachmentMenu = new AttachmentMenu({
      onSelectFromFile: () => this.fileInput.click(),
      onSelectFromScreen: async () => {
        console.log('Requesting screen sources...');
        try {
          // @ts-ignore
          const sources: ScreenSource[] = await window.electronAPI.getScreenSources();
          console.log('Received sources:', sources);
          
          if (sources && sources.length > 0) {
            this.screenSourcePicker.show(sources);
            this.adjustInputHeight();
          } else {
            console.warn('No screen sources were found.');
          }
        } catch (error) {
          console.error('Failed to get screen sources:', error);
          const error_msg = 'Failed to get screen sources:' + error
          NotificationService.showError(error_msg)
        }
      },
      onHide: () => this.adjustInputHeight(),
    });

    this.screenSourcePicker = new ScreenSourcePicker({
      onSelect: async (sourceId: string) => {
        try {
          console.log(`Source selected: ${sourceId}. Capturing high-resolution image...`);
          // @ts-ignore
          const highResDataUrl = await window.electronAPI.captureHighResSource(sourceId);
          if (highResDataUrl) {
            this.attachments.push({
              type: 'screen-capture',
              data: highResDataUrl,
              sourceId: sourceId
            });
            this.renderThumbnails();
            console.log('High-resolution image attached successfully.');
          } else {
             console.warn('Did not receive high-resolution image data.');
          }
        } catch (error) {
          console.error('Failed to capture high-resolution source:', error);
          const error_msg = 'Failed to capture high-resolution source: ' + error;
          NotificationService.showError(error_msg)
        } finally {
            this.adjustInputHeight();
            this.focus();
        }
      },
      onClose: () => {
        this.adjustInputHeight();
        this.focus();
      }
    });

    this.element.prepend(this.attachmentMenu.getElement());
    this.bindEvents();
    this.setupKeyboardShortcuts();
    this.updateUI();
  }

  public getElement(): HTMLElement {
    return this.element;
  }

  private createElement(): HTMLElement {
    const div = document.createElement('div');
    div.className = 'input-area';
    // --- ΑΝΑΔΟΜΗΣΗ ΤΟΥ HTML ---
    div.innerHTML = `
      <div class="input-main-container">
        <textarea
          class="input-field single"
          placeholder="${TEXT.INPUT_PLACEHOLDER}"
          rows="1"
          spellcheck="false"
        ></textarea>
        <div class="input-main-actions">
          <button class="btn btn-record" data-tooltip="Voice input (F2)">
            <svg class="btn-icon microphone-icon" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.49 6-3.31 6-6.72h-1.7z"/>
            </svg>
          </button>
          <button class="btn btn-send" data-tooltip="Send message (Enter)">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
      
      <div class="thumbnails-container"></div>
      <input type="file" class="file-input" accept="image/*,.pdf" multiple style="display: none;" />
      
      <div class="input-toolbar">
        <div class="toolbar-left">
          <button class="btn btn-attach" data-tooltip="Attach file">
            <svg class="btn-icon" viewBox="0 0 24 24">
              <path d="M21.5203125 1.756875c-2.34375-2.3424609375-6.142734375-2.3424609375-8.4849375 0L1.01221875 13.899140625c-0.389578125 0.392578125-0.38775 1.024765625 0.0037890625 1.414453125 0.392578125 0.389578125 1.024765625 0.38775 1.414453125-0.0037890625L14.450390625 3.169189453125c1.560421875-1.560421875 4.09259375-1.560421875 5.655046875 0.002109375 1.56234375 1.56234375 1.56234375 4.0945703125 0 5.6568896484375L7.73025 21.2697265625c-0.97434375 0.9736875-2.557640625 0.9736875-3.534140625-0.002109375-0.97621875-0.97621875-0.97621875-2.5587734375 0.00028125-3.535693359375l10.253953125-10.253953125c0.000328125-0.000328125 0.000609375-0.000703125 0.0009375-0.00103125 0.39084375-0.389578125 1.02234375-0.389296875 1.413703125 0.0009375 0.39084375 0.39084375 0.39084375 1.02434375 0 1.4156640625l-4.953125 4.9541015625c-0.39084375 0.39084375-0.39080078125 1.025625 0.000140625 1.4156640625 0.39084375 0.39084375 1.025625 0.390796875 1.4156640625-0.000140625l4.953125-4.953125c1.171453125-1.171453125 1.171453125-3.0664609375-0.00009375-4.2407578125-1.171546875-1.171546875-3.0665546875-1.171546875-4.24084375 0-0.00065625 0.00065625-0.00121875 0.00140625-0.001875 0.0020625L2.782125 16.317578125c-1.75753125 1.75753125-1.75753125 4.60678125 0 6.3643125 1.75778125 1.7566875 4.60640625 1.7566875 6.3640078125 0.00028125L21.522203125 10.23703125c2.34290625-2.341796875 2.34290625-6.1396875 0-8.48265625z"/>
            </svg>
          </button>
          <button class="btn btn-clear-input" data-tooltip="Clear text and attachments">
             <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
             </svg>
          </button>
        </div>
        <div class="toolbar-right">
          <span class="char-counter">0</span>
          <button class="btn btn-toggle-input" data-tooltip="Toggle input mode (Tab)">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 17h18M3 12h18M3 7h18"/>
            </svg>
          </button>
          <button class="btn btn-history" data-tooltip="Show Conversations (F5)">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
            </svg>
          </button>
          <button class="btn btn-settings" data-tooltip="Settings (F3)">
            <svg class="btn-icon" viewBox="0 0 24 24">
              <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-1.7,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z\"/>
            </svg>
          </button>
        </div>
      </div>
      
      <button class="expand-button" data-tooltip="Show conversation (F4)">
        <svg class="expand-icon" viewBox="0 0 24 24">
          <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z\"/>
        </svg>
      </button>
    `;
    return div;
  }

  private initializeElements(): void {
    this.inputField = this.element.querySelector('.input-field') as HTMLTextAreaElement;
    this.attachButton = this.element.querySelector('.btn-attach') as HTMLButtonElement;
    this.fileInput = this.element.querySelector('.file-input') as HTMLInputElement;
    this.thumbnailsContainer = this.element.querySelector('.thumbnails-container') as HTMLElement;
    this.toggleButton = this.element.querySelector('.btn-toggle-input') as HTMLButtonElement;
    this.recordButton = this.element.querySelector('.btn-record') as HTMLButtonElement;
    this.sendButton = this.element.querySelector('.btn-send') as HTMLButtonElement; // <-- ΝΕΟ
    this.settingsButton = this.element.querySelector('.btn-settings') as HTMLButtonElement;
    this.historyButton = this.element.querySelector('.btn-history') as HTMLButtonElement;
    this.expandButton = this.element.querySelector('.expand-button') as HTMLButtonElement;
    this.clearInputButton = this.element.querySelector('.btn-clear-input') as HTMLButtonElement;
    this.charCounter = this.element.querySelector('.char-counter') as HTMLElement;
    
    this.updateClearButtonVisibility(); // Initial check
  }

  private bindEvents(): void {
    this.inputField.addEventListener('input', this.handleInput.bind(this));
    this.inputField.addEventListener('keydown', this.handleKeyDown.bind(this));
    this.inputField.addEventListener('focus', this.handleFocus.bind(this));
    this.inputField.addEventListener('blur', this.handleBlur.bind(this));
    this.element.addEventListener('drop', this.handleDrop.bind(this));
    this.element.addEventListener('dragover', this.handleDragOver.bind(this));
    this.element.addEventListener('dragenter', this.handleDragEnter.bind(this));
    this.element.addEventListener('dragleave', this.handleDragLeave.bind(this));
    this.attachButton.addEventListener('click', this.handleAttachClick.bind(this));
    this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
    this.toggleButton.addEventListener('click', this.handleToggleInputMode.bind(this));
    this.recordButton.addEventListener('click', this.handleToggleRecording.bind(this));
    this.sendButton.addEventListener('click', this.sendMessage.bind(this)); // <-- ΝΕΟ
    this.settingsButton.addEventListener('click', this.handleOpenSettings.bind(this));
    this.expandButton.addEventListener('click', this.handleToggleConversation.bind(this));
    this.historyButton.addEventListener('click', this.handleToggleHistory.bind(this));
    this.clearInputButton.addEventListener('click', this.handleClearInput.bind(this));
  }

  private async handleClearInput(): Promise<void> {
    if (!this.inputField.value.trim() && this.attachments.length === 0) {
      return;
    }
    this.clearInput();
    // try {
    //   await ConfirmationModal.show({
    //     title: 'Clear Input',
    //     message: 'Are you sure you want to clear all text and remove all attachments?',
    //     confirmText: 'Clear',
    //     cancelText: 'Cancel'
    //   });
    //   this.clearInput();
    // } catch {
    //   console.log('Input clearing was cancelled.');
    // }
  }

  private handleAttachClick(): void {
    const rect = this.attachButton.getBoundingClientRect();
    this.attachmentMenu.show(rect);
    this.adjustInputHeight();
  }
  
  private handleDragEnter(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.element.classList.add('dragging-over');
  }

  private handleDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.element.classList.add('dragging-over');
  }

  private handleDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    if (this.element.contains(event.relatedTarget as Node)) {
        return;
    }
    this.element.classList.remove('dragging-over');
  }

  private handleDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.element.classList.remove('dragging-over');
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFiles(files);
    }
  }

  private handleFileSelect(event: Event): void {
    const files = (event.target as HTMLInputElement).files;
    if (!files) return;
    this.handleFiles(files);
    this.fileInput.value = '';
  }

  private async handleFiles(files: FileList): Promise<void> {
    for (const file of Array.from(files)) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const result = e.target?.result as string;
        if (file.type.startsWith('image/')) {
          this.attachments.push({ type: 'image', data: result });
          this.renderThumbnails();
        } else if (file.type === 'application/pdf') {
          const tempId = `pdf_${Date.now()}`;
          const tempAttachment = { type: 'pdf', data: '', filename: file.name, tempId };
          this.renderPdfThumbnail(tempAttachment, true);
          try {
            // @ts-ignore
            const response = await window.electronAPI.processPdfAttachment(result);
            
            if (response.success) {
              this.attachments.push({
                type: 'pdf',
                data: result,
                filename: file.name,
                extractedText: response.data.extractedText ?? undefined,
              });
            } else {
              console.error('PDF processing failed:', response.error);
              const error_msg = "PDF processing failed. " + response.error
              NotificationService.showError(error_msg)
              
            }
          } catch (error) {
            console.error("IPC call for PDF processing failed: ", error);
            const error_msg = "IPC call for PDF processing failed: " + error;
            NotificationService.showError(error_msg)
          } finally {
             this.renderThumbnails();
          }
        }
      };
      reader.readAsDataURL(file);
    }
  }

  private renderPdfThumbnail(att: any, isProcessing: boolean): void {
      const thumbWrapper = document.createElement('div');
      thumbWrapper.className = 'thumbnail-wrapper thumbnail-pdf-wrapper';
      if (isProcessing) {
          thumbWrapper.classList.add('processing');
      }
      thumbWrapper.innerHTML = `
          <div class="thumbnail-pdf-icon">
              ${isProcessing 
                  ? `<div class="spinner"></div>`
                  : `<svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM9 17v-2h6v2H9zm4-4H9v-2h4v2zm-2-4H9V7h2v2z"/></svg>`
              }
          </div>
          <span class="thumbnail-pdf-filename">${att.filename}</span>
      `;
      if (!isProcessing) {
          const removeBtn = document.createElement('button');
          removeBtn.className = 'thumbnail-remove-btn';
          removeBtn.innerHTML = '&times;';
          removeBtn.onclick = () => {
              const realIndex = this.attachments.findIndex(a => a.type === 'pdf' && a.filename === att.filename);
              if (realIndex > -1) {
                  this.attachments.splice(realIndex, 1);
                  this.renderThumbnails();
              }
          };
          thumbWrapper.appendChild(removeBtn);
      }
      
      const existingThumb = this.thumbnailsContainer.querySelector(`[data-tempid="${att.tempId}"]`);
      if (existingThumb) {
          existingThumb.replaceWith(thumbWrapper);
      } else {
          thumbWrapper.setAttribute('data-tempid', att.tempId);
          this.thumbnailsContainer.appendChild(thumbWrapper);
      }
  }

   private renderThumbnails(): void {
    this.thumbnailsContainer.innerHTML = '';
    if (this.attachments.length > 0) {
      this.thumbnailsContainer.style.display = 'flex';
    } else {
      this.thumbnailsContainer.style.display = 'none';
    }
    this.updateClearButtonVisibility();
    this.attachments.forEach((att, index) => {
      const thumbWrapper = document.createElement('div');
      thumbWrapper.className = 'thumbnail-wrapper';
      if (att.type === 'image' || att.type === 'screen-capture') {
        thumbWrapper.classList.add('thumbnail-image-wrapper');
        const img = document.createElement('img');
        img.src = att.data;
        img.className = 'thumbnail-image';
        thumbWrapper.appendChild(img);
      } else if (att.type === 'pdf') {
        thumbWrapper.classList.add('thumbnail-pdf-wrapper');
        thumbWrapper.innerHTML = `
          <div class="thumbnail-pdf-icon">
            <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM9 17v-2h6v2H9zm4-4H9v-2h4v2zm-2-4H9V7h2v2z"/></svg>
          </div>
          <span class="thumbnail-pdf-filename">${att.filename}</span>
        `;
      }
      
      const removeBtn = document.createElement('button');
      removeBtn.className = 'thumbnail-remove-btn';
      removeBtn.innerHTML = '&times;';
      removeBtn.onclick = () => {
        this.attachments.splice(index, 1);
        this.renderThumbnails();
      };
      thumbWrapper.appendChild(removeBtn);
      this.thumbnailsContainer.appendChild(thumbWrapper);
    });
    this.adjustInputHeight();
  }

  private setupKeyboardShortcuts(): void {
    document.addEventListener('keydown', this.handleGlobalKeyDown.bind(this));
  }

  private handleInput(): void {
    const value = this.inputField.value;
    this.updateCharCounter(value.length);
    this.adjustInputHeight();
    this.updateClearButtonVisibility();
  }

  private handleKeyDown(e: KeyboardEvent): void {
    if (e.key === 'Enter') {
      if (this.inputMode === InputMode.SINGLE_LINE || !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    } else if (e.key === 'Tab' && !e.shiftKey) {
      e.preventDefault();
      this.toggleInputMode();
    }
  }

  private handleFocus(): void {
    this.element.classList.add('focused');
  }

  private handleBlur(): void {
    this.element.classList.remove('focused');
  }

  private handleToggleInputMode(): void {
    this.toggleInputMode();
  }

  private handleToggleRecording(): void {
    this.callbacks.onToggleRecording?.();
  }

  private handleOpenSettings(): void {
    this.callbacks.onOpenSettings?.();
  }

  private handleToggleConversation(): void {
    this.callbacks.onToggleConversation?.();
  }

  private handleToggleHistory(): void {
    this.callbacks.onToggleHistory?.();
  }

  private handleGlobalKeyDown(e: KeyboardEvent): void {
    // Global keydown logic...
  }

  private sendMessage(): void {
    const messageText = this.inputField.value.trim();
    if (messageText || this.attachments.length > 0) {
      this.callbacks.onSendMessage?.({
        text: messageText,
        attachments: this.attachments,
      });
      this.clearInput();
    }
  }

  private toggleInputMode(): void {
    this.inputMode = this.inputMode === InputMode.SINGLE_LINE 
      ? InputMode.MULTI_LINE 
      : InputMode.SINGLE_LINE;
    
    this.updateInputMode();
    this.callbacks.onInputModeChange?.(this.inputMode);
  }

  private updateInputMode(): void {
    this.inputField.className = `input-field ${this.inputMode === InputMode.SINGLE_LINE ? 'single' : 'multi'}`;
    const toggleButtonIcon = this.toggleButton.querySelector('.btn-icon') as SVGElement;
    
    if (this.inputMode === InputMode.SINGLE_LINE) {
      this.inputField.rows = 1;
      toggleButtonIcon.innerHTML = `<path d="M3 17h18M3 12h18M3 7h18"/>`;
      this.toggleButton.dataset.tooltip = 'Switch to multi-line (Shift+Enter for newline)';
    } else {
      this.inputField.rows = 1; // It will auto-grow
      toggleButtonIcon.innerHTML = `<path d="M3 15h18v-2H3v2zm0 4h18v-2H3v2zm0-8h18V9H3v2zm0-6v2h18V5H3z"/>`;
      this.toggleButton.dataset.tooltip = 'Switch to single-line (Enter to send)';
    }
    this.adjustInputHeight();
  }

  private adjustInputHeight(): void {
    const input = this.inputField;
    input.style.height = 'auto';
    input.style.height = `${input.scrollHeight}px`;
    
    this.callbacks.onInputWindowResize?.();
  }
  
  public setInputFieldHeight(new_height: number): void {
      this.inputField.style.height = new_height + 'px';
  }
  
  public getInputAreaHeight(): { input_area: number; input_field: number } {
      const inputFieldHeight = this.inputField.scrollHeight;
      if (this.screenSourcePicker.isVisible()) {
        return {
          input_area: WINDOW_SIZE.SCREEN_SOURCE_PICKER_HEIGHT,
          input_field: inputFieldHeight
        };
      }
      const baseHeight = this.element.scrollHeight;
      let totalRequiredHeight = baseHeight;
      if (this.attachmentMenu.isVisible()) {
          const menuHeight = this.attachmentMenu.getMenuHeight();
          const heightForMenu = baseHeight + menuHeight;
          totalRequiredHeight = Math.max(totalRequiredHeight, heightForMenu);
      }
      
      return { input_area: totalRequiredHeight, input_field: inputFieldHeight };
  }

  private updateCharCounter(count: number): void {
    this.charCounter.textContent = count.toString();
    this.charCounter.className = 'char-counter';
    if (count > 3000) this.charCounter.classList.add('warning');
    if (count > 4000) this.charCounter.classList.add('error');
  }

  private updateExpandButton(): void {
    this.expandButton.classList.toggle('expanded', this.isExpanded);
  }

  private updateUI(): void {
    this.updateInputMode();
    this.updateRecordingState();
  }
  
  private updateRecordingState(): void {
    this.recordButton.classList.remove('recording', 'processing', 'active');
    this.recordButton.disabled = false;
    
    switch (this.recordingState) {
      case RecordingState.IDLE:
        this.recordButton.innerHTML = `
          <svg class="btn-icon microphone-icon" viewBox="0 0 24 24">
            <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.49 6-3.31 6-6.72h-1.7z"/>
          </svg>`;
        break;
      case RecordingState.RECORDING:
        this.recordButton.classList.add('recording', 'active');
        this.recordButton.innerHTML = `
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="6" y="6" width="12" height="12" rx="2"/>
          </svg>`;
        break;
      case RecordingState.PROCESSING:
        this.recordButton.classList.add('processing', 'active');
        this.recordButton.disabled = true;
        this.recordButton.innerHTML = `<div class="spinner"></div>`;
        break;
    }
  }

  public setRecordingState(state: RecordingState): void {
    this.recordingState = state;
    this.updateRecordingState();
  }

  public setValue(value: string): void {
    this.inputField.value = value;
    this.updateCharCounter(value.length);
    this.adjustInputHeight();
  }

  public getValue(): string {
    return this.inputField.value;
  }

  public clearInput(): void {
    this.inputField.value = '';
    this.attachments = [];
    this.renderThumbnails(); // This already calls updateClearButtonVisibility
    this.updateCharCounter(0);
    this.adjustInputHeight();
    this.updateClearButtonVisibility();
  }

  public focus(): void {
    this.inputField.focus();
  }

  public setExpanded(expanded: boolean): void {
    this.isExpanded = expanded;
    this.updateExpandButton();
  }

  public getInputMode(): InputMode {
    return this.inputMode;
  }

  public getRecordingState(): RecordingState {
    return this.recordingState;
  }

  public isInputExpanded(): boolean {
    return this.isExpanded;
  }

  public getDimensions(): { width: number; height: number } {
    const rect = this.element.getBoundingClientRect();
    return {
      width: rect.width,
      height: rect.height,
    };
  }

  public setCallbacks(callbacks: InputAreaCallbacks): void {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  private updateClearButtonVisibility(): void {
    const hasContent = this.inputField.value.length > 0 || this.attachments.length > 0;
    if (hasContent) {
      this.clearInputButton.classList.add('visible');
    } else {
      this.clearInputButton.classList.remove('visible');
    }
  }

  public destroy(): void {
    document.removeEventListener('keydown', this.handleGlobalKeyDown.bind(this));
    
    this.inputField.removeEventListener('input', this.handleInput.bind(this));
    this.inputField.removeEventListener('keydown', this.handleKeyDown.bind(this));
    this.inputField.removeEventListener('focus', this.handleFocus.bind(this));
    this.inputField.removeEventListener('blur', this.handleBlur.bind(this));
    this.element.removeEventListener('drop', this.handleDrop.bind(this));
    this.element.removeEventListener('dragover', this.handleDragOver.bind(this));
    this.element.removeEventListener('dragenter', this.handleDragEnter.bind(this));
    this.element.removeEventListener('dragleave', this.handleDragLeave.bind(this));
    this.attachButton.removeEventListener('click', this.handleAttachClick.bind(this));
    this.fileInput.removeEventListener('change', this.handleFileSelect.bind(this));
    this.toggleButton.removeEventListener('click', this.handleToggleInputMode.bind(this));
    this.recordButton.removeEventListener('click', this.handleToggleRecording.bind(this));
    this.sendButton.removeEventListener('click', this.sendMessage.bind(this)); // <-- ΝΕΟ
    this.settingsButton.removeEventListener('click', this.handleOpenSettings.bind(this));
    this.expandButton.removeEventListener('click', this.handleToggleConversation.bind(this));
    this.historyButton.removeEventListener('click', this.handleToggleHistory.bind(this));
    this.clearInputButton.removeEventListener('click', this.handleClearInput.bind(this));
    
    this.element.remove();
  }

  public async loadSttConfig(): Promise<void> {
    try {
      // @ts-ignore
      const config = await window.electronAPI.loadConfig();
      if (!config.stt?.enabled) {
        this.recordButton.disabled = true;
        this.recordButton.dataset.tooltip = 'Voice input is disabled in settings.';
      } else {
        this.recordButton.disabled = false;
        this.recordButton.dataset.tooltip = 'Voice input (F2)';
      }
    } catch (error) {
      console.error('Failed to load STT configuration:', error);
      const error_msg = 'Failed to load STT configuration: '+ error;
      NotificationService.showError(error_msg)
      this.recordButton.disabled = true;
      this.recordButton.dataset.tooltip = 'Error loading voice settings.';
    }
  }
}