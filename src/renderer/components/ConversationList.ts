// src/renderer/components/ConversationList.ts
import { Conversation } from '@shared/types';
import '../styles/components/conversation-list.css';
import { ConfirmationModal } from '@renderer/services/ConfirmationService';
import { NotificationService } from '@renderer/services/NotificationService';

// Callbacks for the List to communicate with the ChatWindow
export interface ConversationListCallbacks {
  onConversationSelect: (conversationId: string) => void;
  onConversationDelete: (conversationId: string) => void;
  onNewConversation: () => void;
  onClearAll: () => void;
  onCloseList: () => void;
}

export class ConversationList {
  private element: HTMLElement;
  private conversationListElement: HTMLElement;
  private callbacks: ConversationListCallbacks;
  private isVisible = false;
  private activeConversationId: string | null = null;

  constructor(callbacks: ConversationListCallbacks) {
    this.callbacks = callbacks;
    this.element = this.createElement();
    this.conversationListElement = this.element.querySelector('.conversation-list-items') as HTMLElement;
    this.bindEvents();
  }

  private createElement(): HTMLElement {
    const sidebar = document.createElement('div');
    sidebar.className = 'conversation-history-sidebar';
    sidebar.innerHTML = `
      <div class="sidebar-header">
        <h2 class="sidebar-title">History</h2>
        <div class="sidebar-header-buttons">
          <button class="btn btn-new-chat" title="New Conversation">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 5v14m-7-7h14" />
            </svg>
          </button>
          <button class="btn btn-clear-all" title="Clear All Conversations">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18m-2 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m-6 5v6m4-6v6"/>
            </svg>
          </button>
          <button class="btn btn-close-list" title="Close List">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M18 6L6 18M6 6l12 12" />
            </svg>
        </button>
        </div>
      </div>
      <div class="sidebar-content">
        <ul class="conversation-list-items"></ul>
      </div>
    `;
    return sidebar;
  }

  private bindEvents(): void {
    const newChatButton = this.element.querySelector('.btn-new-chat');
    newChatButton?.addEventListener('click', () => {
      this.callbacks.onNewConversation();
    });
    const clearAllButton = this.element.querySelector('.btn-clear-all');
    clearAllButton?.addEventListener('click', async () => {
      try {
        await ConfirmationModal.show({
          title: 'Clear All History',
          message: 'Are you sure you want to delete ALL conversations? This action cannot be undone.',
          confirmText: 'Yes, Clear All'
        });
        this.callbacks.onClearAll();
        NotificationService.showSuccess('All conversations have been deleted.');

      } catch (error) {
        if (error) {
          NotificationService.showError(`An error occurred: ${error}`);
        } else {
          console.log('Clear all was cancelled by the user.');
        }
      }
    });

    const closeListButton = this.element.querySelector('.btn-close-list');
    closeListButton?.addEventListener('click', () => {
      this.callbacks.onCloseList();
    });
  }

  public getElement(): HTMLElement {
    return this.element;
  }

  public setActiveConversation(conversationId: string | null): void {
    this.activeConversationId = conversationId;
    this.conversationListElement.querySelectorAll('.conversation-item').forEach(item => {
      const id = item.getAttribute('data-id');
      if (id === this.activeConversationId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }
  public render(conversations: Conversation[]): void {
    this.conversationListElement.innerHTML = '';

    const sortedConversations = [...conversations].sort((a, b) =>
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );

    if (sortedConversations.length === 0) {
      this.conversationListElement.innerHTML = `<li class="empty-list-message">No conversations yet.</li>`;
      return;
    }

    sortedConversations.forEach(conv => {
      const item = document.createElement('li');
      item.className = 'conversation-item';
      if (conv.id === this.activeConversationId) {
        item.classList.add('active');
      }
      item.setAttribute('data-id', conv.id);

      const formattedDate = new Date(conv.updatedAt).toLocaleDateString(undefined, {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });

      item.innerHTML = `
        <div class="item-content">
          <span class="item-title">${conv.title}</span>
          <span class="item-date">${formattedDate}</span>
        </div>
        <button class="btn btn-delete-chat" title="Delete Conversation">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      `;

      item.querySelector('.item-content')?.addEventListener('click', (e) => {
        console.log("clicked");
        e.stopPropagation();
        this.callbacks.onConversationSelect(conv.id);
      });

      item.querySelector('.btn-delete-chat')?.addEventListener('click', async (e) => {
        e.stopPropagation();
        try {
          await ConfirmationModal.show({
            title: 'Delete Conversation',
            message: `Are you sure you want to delete "${conv.title}"?`,
            confirmText: 'Delete'
          });

          this.callbacks.onConversationDelete(conv.id);

        } catch (error) {
          if (error) {
            NotificationService.showError(`Could not delete conversation: ${error}`);
          } else {
            console.log('Conversation deletion cancelled.');
          }
        }
      });
      
      this.conversationListElement.appendChild(item);
    });
  }

  public show(): void {
    this.element.classList.add('visible');
    this.isVisible = true;
  }

  public hide(): void {
    this.element.classList.remove('visible');
    this.isVisible = false;
  }

  public toggle(): boolean {
    this.isVisible ? this.hide() : this.show();
    return this.isVisible;
  }
}