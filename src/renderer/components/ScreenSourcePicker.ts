// src/renderer/components/ScreenSourcePicker.ts
import '../styles/components/screen-source-picker.css';
import { ScreenSource } from '@shared/types';

interface ScreenSourcePickerCallbacks {
  onSelect: (sourceId: string) => void;
  onClose: () => void;
}

export class ScreenSourcePicker {
  private element: HTMLElement;
  private sourceList: HTMLElement;
  private callbacks: ScreenSourcePickerCallbacks;

  constructor(callbacks: ScreenSourcePickerCallbacks) {
    this.callbacks = callbacks;
    this.element = this.createElement();
    this.sourceList = this.element.querySelector('.source-list') as HTMLElement;
    this.bindEvents();
    document.body.appendChild(this.element);
  }

  private createElement(): HTMLElement {
    const picker = document.createElement('div');
    picker.className = 'screen-picker-overlay';
    picker.innerHTML = `
      <div class="screen-picker-window">
        <div class="screen-picker-header">
          <h2>Select a Screen or Window</h2>
          <button class="btn-close-picker">&times;</button>
        </div>
        <div class="source-list"></div>
      </div>
    `;
    return picker;
  }

  private bindEvents(): void {
    this.element.querySelector('.btn-close-picker')?.addEventListener('click', () => this.hide());
    // Closing the modal by clicking on the overlay
    this.element.addEventListener('click', (e) => {
      if (e.target === this.element) {
        this.hide();
      }
    });
  }

  public show(sources: ScreenSource[]): void {
    this.sourceList.innerHTML = '';
    sources.forEach(source => {
      const sourceItem = document.createElement('div');
      sourceItem.className = 'source-item';
      sourceItem.dataset.id = source.id;
      sourceItem.innerHTML = `
        <div class="source-thumbnail-wrapper">
          <img src="${source.thumbnail}" class="source-thumbnail" alt="${source.name}"/>
        </div>
        <div class="source-name">${source.name}</div>
      `;
      sourceItem.addEventListener('click', () => {
        this.callbacks.onSelect(source.id); 
        this.hide();
      });
      this.sourceList.appendChild(sourceItem);
    });
    this.element.classList.add('visible');
  }

  public isVisible(): boolean {
      return this.element.classList.contains('visible');
  }

  public hide(): void {
    this.element.classList.remove('visible');
    this.callbacks.onClose();
  }

  public destroy(): void {
    document.body.removeChild(this.element);
  }
}