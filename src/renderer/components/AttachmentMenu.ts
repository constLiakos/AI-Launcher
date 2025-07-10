// src/renderer/components/AttachmentMenu.ts
import '@renderer/styles/components/attachment-menu.css';

interface AttachmentMenuCallbacks {
  onSelectFromFile: () => void;
  onSelectFromScreen: () => void;
  onHide: () => void;
}

export class AttachmentMenu {
  private element: HTMLElement;
  private callbacks: AttachmentMenuCallbacks;

  constructor(callbacks: AttachmentMenuCallbacks) {
    this.callbacks = callbacks;
    this.element = this.createElement();
    this.bindEvents();
    document.addEventListener('click', this.handleDocumentClick.bind(this), true);
  }

  public getElement(): HTMLElement {
    return this.element;
  }

  private createElement(): HTMLElement {
    const menu = document.createElement('div');
    menu.className = 'attachment-menu';
    menu.innerHTML = `
      <ul>
        <li data-action="file">Select from files</li>
        <li data-action="screen">Share screen</li>
      </ul>
    `;
    return menu;
  }

  private bindEvents(): void {
    this.element.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      const action = target.closest('li')?.dataset.action;

      if (action === 'file') {
        this.callbacks.onSelectFromFile();
        this.hide();
      } else if (action === 'screen') {
        this.callbacks.onSelectFromScreen();
        this.hide();
      }
    });
  }

  /**
   * Shows the attachment menu positioned relative to a DOMRect (typically the attach button).
   * @param rect The DOMRect of the element to position against.
   */
  public show(rect: DOMRect): void {
    // Position the menu to drop down from the button
    this.element.style.left = `${rect.left}px`;
    this.element.style.top = `${rect.bottom + 8}px`; // Position below the button with a small gap
    this.element.classList.add('visible');
  }

  public hide(): void {
    this.element.classList.remove('visible');
    this.callbacks.onHide();
  }

  public getMenuHeight(): number {
    return this.element.classList.contains('visible') ? this.element.offsetHeight : 0;
  }

  public isVisible(): boolean {
      return this.element.classList.contains('visible');
  }
  
  private handleDocumentClick(event: MouseEvent): void {
    const target = event.target as Node;
    // Hide if the click is outside the menu AND not on the attach button itself
    if (this.isVisible() && !this.element.contains(target) && !(target instanceof Element && target.closest('.btn-attach'))) {
        this.hide();
        // We might need to trigger a resize if the menu is closed this way
        // This requires a callback to InputArea, which adds complexity.
        // For now, we assume this is handled elsewhere if needed.
    }
  }

  public destroy(): void {
    document.removeEventListener('click', this.handleDocumentClick.bind(this), true);
    this.element.remove();
  }
}