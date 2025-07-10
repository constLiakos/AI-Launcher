// src/renderer/services/ConfirmationService.ts

interface ConfirmationOptions {
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
}

class ConfirmationModalController {
    private modalElement!: HTMLElement;
    private titleElement!: HTMLElement;
    private messageElement!: HTMLElement;
    private confirmButton!: HTMLButtonElement;
    private cancelButton!: HTMLButtonElement;
    private isInitialized = false;

    constructor() {}

    /**
     * Initializes the modal by creating its HTML in the DOM.
     * Must be called once when the main application view is ready.
     */
    public init(): void {
        if (this.isInitialized) return;

        this.createModalInDOM();

        this.modalElement = document.getElementById('global-confirm-modal') as HTMLElement;
        this.titleElement = this.modalElement.querySelector('.modal-title') as HTMLElement;
        this.messageElement = this.modalElement.querySelector('.modal-message') as HTMLElement;
        this.confirmButton = this.modalElement.querySelector('.confirm-btn') as HTMLButtonElement;
        this.cancelButton = this.modalElement.querySelector('.cancel-btn') as HTMLButtonElement;
        
        this.isInitialized = true;
    }

    public show(options: ConfirmationOptions): Promise<void> {
        if (!this.isInitialized) {
            console.error('ConfirmationModal has not been initialized. Call init() first.');
            // Fallback to window.confirm if not initialized
            if (window.confirm(`${options.title}\n\n${options.message}`)) {
                return Promise.resolve();
            } else {
                return Promise.reject();
            }
        }

        return new Promise((resolve, reject) => {
            this.titleElement.textContent = options.title;
            this.messageElement.textContent = options.message;
            this.confirmButton.textContent = options.confirmText || 'Confirm';
            this.cancelButton.textContent = options.cancelText || 'Cancel';

            const onConfirm = () => {
                cleanup();
                resolve();
            };

            const onCancel = () => {
                cleanup();
                reject();
            };
            
            const cleanup = () => {
                this.hide();
                this.confirmButton.removeEventListener('click', onConfirm);
                this.cancelButton.removeEventListener('click', onCancel);
            };

            this.confirmButton.addEventListener('click', onConfirm, { once: true });
            this.cancelButton.addEventListener('click', onCancel, { once: true });

            this.modalElement.style.display = 'flex';
        });
    }

    private hide(): void {
        this.modalElement.style.display = 'none';
    }

    private createModalInDOM(): void {
        if (document.getElementById('global-confirm-modal')) return;
        const modalHTML = `
            <div id="global-confirm-modal" style="display: none;">
                <div class="modal-content small-modal">
                    <h4 class="modal-title"></h4>
                    <p class="modal-message"></p>
                    <div class="modal-actions">
                        <button class="btn cancel-btn"></button>
                        <button class="btn confirm-btn"></button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
}

export const ConfirmationModal = new ConfirmationModalController();