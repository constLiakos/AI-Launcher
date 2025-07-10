import { Message, Conversation, Attachment } from '@shared/types';
import { parseMarkdown } from '@renderer/utils/markdownParser';

export class ConversationArea {
  private element: HTMLElement;
  private header: HTMLElement;
  private content: HTMLElement;
  private messageContainer: HTMLElement;
  private contextMenu: HTMLElement;
  private isVisible: boolean = false;
  private activeMessageElement: HTMLElement | null = null;
  private userHasScrolled: boolean = false;

  private onClearConversation?: () => void;
  private onNewConversation?: () => void;

  constructor() {
    this.element = this.createElement();
    this.contextMenu = this.createContextMenuElement();
    document.body.appendChild(this.contextMenu);

    this.header = this.element.querySelector('.conversation-header') as HTMLElement;
    this.content = this.element.querySelector('.conversation-content') as HTMLElement;
    this.messageContainer = this.element.querySelector('.message-container') as HTMLElement;

    this.bindEvents();
  }

  public getElement(): HTMLElement {
    return this.element;
  }

  private createElement(): HTMLElement {
    const div = document.createElement('div');
    div.className = 'conversation-area';
    div.innerHTML = `
      <div class="conversation-header">
        <div class="conversation-title">Conversation</div>
        <div class="conversation-actions">
          <button class="btn btn-new-conversation" data-tooltip="New conversation">
            <svg class="btn-icon" viewBox="0 0 24 24">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
          </button>
          <button class="btn btn-clear-conversation" data-tooltip="Clear conversation">
            <svg class="btn-icon" viewBox="0 0 24 24">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="conversation-content">
        <div class="message-container">
          <div class="message-placeholder">
            Start a conversation by typing a message above
          </div>
        </div>
      </div>
    `;
    return div;
  }

  private createContextMenuElement(): HTMLElement {
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.innerHTML = `
      <div class="context-menu-item" id="copy-text">Copy</div>
      <div class="context-menu-item" id="select-all">Select All</div>
    `;
    return menu;
  }

private bindEvents(): void {
    const newBtn = this.header.querySelector('.btn-new-conversation') as HTMLButtonElement;
    const clearBtn = this.header.querySelector('.btn-clear-conversation') as HTMLButtonElement;

    newBtn.addEventListener('click', () => this.onNewConversation?.());
    clearBtn.addEventListener('click', () => this.onClearConversation?.());
    this.messageContainer.addEventListener('click', this.handleAttachmentClick.bind(this));

    this.messageContainer.addEventListener('contextmenu', this.showContextMenu.bind(this));
    document.addEventListener('click', this.hideContextMenu.bind(this));
    this.contextMenu.addEventListener('click', this.handleContextMenuClick.bind(this));

    this.messageContainer.addEventListener('scroll', () => {
        const buffer = 15;
        const isNearBottom = this.messageContainer.scrollTop + this.messageContainer.clientHeight >= this.messageContainer.scrollHeight - buffer;
        this.userHasScrolled = !isNearBottom;
    }, { passive: true });
}

  private showContextMenu(event: MouseEvent): void {
    event.preventDefault();
    this.activeMessageElement = (event.target as HTMLElement).closest('.message-content');
    if (!this.activeMessageElement) {
        this.hideContextMenu();
        return;
    }
    const selection = window.getSelection()?.toString().trim();
    const copyButton = this.contextMenu.querySelector('#copy-text') as HTMLElement;

    this.contextMenu.style.top = `${event.clientY}px`;
    this.contextMenu.style.left = `${event.clientX}px`;
    this.contextMenu.style.display = 'block';
  }

  private hideContextMenu(): void {
    this.contextMenu.style.display = 'none';
    this.activeMessageElement = null;
  }

  private handleContextMenuClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (target.id === 'copy-text' && this.activeMessageElement) {
      const selection = window.getSelection()?.toString().trim();

      if (selection) {
        navigator.clipboard.writeText(selection);
      } else {
        const messageTextElement = this.activeMessageElement.querySelector('.message-text') as HTMLElement;
        if (messageTextElement) {
          navigator.clipboard.writeText(messageTextElement.innerText);
        }
      }
    } else if (target.id === 'select-all') {
        if (this.activeMessageElement) {
            const range = document.createRange();
            const messageTextElement = this.activeMessageElement.querySelector('.message-text');
            if (messageTextElement) {
                range.selectNodeContents(messageTextElement);
                window.getSelection()?.removeAllRanges();
                window.getSelection()?.addRange(range);
            }
        }
    }
    this.hideContextMenu();
  }


  private handleAttachmentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    const downloadButton = target.closest('.attachment-download-btn');
    if (downloadButton) {
        const container = downloadButton.closest('.attachment-container');
        if(!container) return;

        let dataUrl: string | undefined;
        const filename = downloadButton.getAttribute('data-filename') || 'download';

        if (container.classList.contains('attachment-pdf')) {
            console.warn("Download logic for PDF needs implementation to get dataUrl.");
        } else {
            const img = container.querySelector('.attachment-image') as HTMLImageElement;
            if (img) dataUrl = img.src;
        }

        if (dataUrl) {
            window.electronAPI.downloadAttachment({dataUrl, filename});
        }
    }
  }

  public show(): void {
    this.isVisible = true;
    this.element.classList.add('visible');
  }

  public hide(): void {
    this.isVisible = false;
    this.element.classList.remove('visible');
  }

  public toggle(): boolean {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
    return this.isVisible;
  }

  public isElementVisible(): boolean {
    return this.isVisible;
  }


public addMessage(message: Message): void {
    const placeholder = this.messageContainer.querySelector('.message-placeholder');
    if (placeholder) {
      placeholder.remove();
    }

    const messageElement = this.createMessageElement(message);
    this.messageContainer.appendChild(messageElement);
    setTimeout(() => this.autoScrollToBottom(), 100);
    // Attach event listeners to the toggle buttons for thinking content
    messageElement.querySelectorAll('.think-toggle-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const thinkContent = (event.target as HTMLElement).closest('.think-container');
            if (thinkContent) {
                thinkContent.classList.toggle('collapsed');
            }
        });
    });
}

  private createMessageElement(message: Message): HTMLElement {
    const div = document.createElement('div');
    div.className = `message message-${message.role}`;
    div.dataset.messageId = message.id;

    let attachmentsHTML = '';
    if (message.attachments && message.attachments.length > 0) {
      attachmentsHTML = `<div class="message-attachments">`;
      message.attachments.forEach(att => {
        if (att.type === 'image' || att.type === 'screen-capture') {
          attachmentsHTML += `
            <div class="attachment-container">
              <img src="${att.data}" class="attachment-image" alt="User attachment">
              <button class="attachment-download-btn" data-url="${att.data}" data-filename="attachment.png">
                <svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
              </button>
            </div>
          `;
        } else if (att.type === 'pdf') {
          attachmentsHTML += `
            <div class="attachment-container attachment-pdf">
              <div class="attachment-pdf-icon">
                <svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM9 17v-2h6v2H9zm4-4H9v-2h4v2zm-2-4H9V7h2v2z"/></svg>
              </div>
              <div class="attachment-pdf-info">
                <span class="attachment-pdf-filename">${att.filename}</span>
                <button class="attachment-download-btn" data-url="${att.data}" data-filename="${att.filename}">
                  Download PDF
                </button>
              </div>
            </div>
          `;
        }
      });
      attachmentsHTML += `</div>`;
    }
    const errorHTML = message.error !== undefined
      ? `<div class="message-error-box">
           <span class="error-icon">⚠️</span>
           <span class="error-text">${message.error}</span>
         </div>`
      : '<div class="message-error-box">';
    

    div.innerHTML = `
      <div class="message-avatar">
        <svg class="message-icon" viewBox="0 0 24 24">
          ${message.role === 'user'
        ? '<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>'
        : '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>'
      }
        </svg>
      </div>
      <div class="message-content">
        ${attachmentsHTML}
        ${message.content ? `<div class="message-text">${this.formatMessageContent(message.content, false)}</div>` : ''}
        ${errorHTML}
        <div class="message-time">${this.formatTime(message.createdAt)}</div>
      </div>
    `;
    return div;
  }

  public updateMessageContent(messageId: string, newContent: string) {
    const messageElement = this.messageContainer.querySelector(`[data-message-id="${messageId}"]`);
    if (messageElement) {
      const textElement = messageElement.querySelector('.message-text');
      if (textElement) {
        textElement.innerHTML = this.formatMessageContent(newContent, true);
        this.autoScrollToBottom();
      }
    }
  }
  public updateMessageError(messageId: string, error: string) {
    const messageElement = this.messageContainer.querySelector(`[data-message-id="${messageId}"]`);
    const errorHTML = `<div class="message-error-box">
           <span class="error-icon">⚠️</span>
           <span class="error-text">${error}</span>
         </div>`;
    console.log("messageElement: ");
    console.log(messageElement);
    if (messageElement) {
      const messageErrorBox = messageElement.querySelector('.message-error-box');
      console.log("MessageErrorBox: ");
      console.log(messageErrorBox);
      if (messageErrorBox) {
        messageErrorBox.innerHTML = this.formatMessageContent(errorHTML);
        this.autoScrollToBottom();
      }
      else{
      }
    }
  }
  private formatMessageContent(content: string, show_think?:boolean): string {
    return parseMarkdown(content, show_think);
  }

  private formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  private autoScrollToBottom(): void {
    if (!this.userHasScrolled) {
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }
  }
  
  public resetScrollState(): void {
    this.userHasScrolled = false;
    this.autoScrollToBottom();
  }


  public clearMessages(): void {
    this.messageContainer.innerHTML = `
      <div class="message-placeholder">
        Start a conversation by typing a message above
      </div>
    `;
    this.resetScrollState();
  }

  public loadConversation(conversation: Conversation): void {
    this.clearMessages();
    conversation.messages.forEach(message => this.addMessage(message));
    this.resetScrollState();
  }

  public onClear(callback: () => void): void {
    this.onClearConversation = callback;
  }

  public onNew(callback: () => void): void {
    this.onNewConversation = callback;
  }

  public destroy(): void {
    this.element.remove();
    this.contextMenu.remove();
  }
}