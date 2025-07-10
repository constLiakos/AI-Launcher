// src/renderer/services/NotificationService.ts

class NotificationServiceController {
    private container: HTMLElement | null = null;

    /**
     * Initializes the service by specifying the container where notifications will be appended.
     * This should be called once when the application starts.
     * @param containerElement The DOM element to host the notifications.
     */
    public init(containerElement: HTMLElement): void {
        this.container = containerElement;
    }

    /**
     * Shows a success toast message.
     * @param message The message to display.
     */
    public showSuccess(message: string): void {
        this.showToast(message, 'success');
    }

    /**
     * Shows an error toast message.
     * @param message The message to display.
     */
    public showError(message: string): void {
        this.showToast(message, 'error');
    }

    private showToast(message: string, type: 'success' | 'error'): void {
        if (!this.container) {
            console.error('NotificationService not initialized. Call init() first.');
            // Fallback to alert if not initialized
            alert(`[${type.toUpperCase()}] ${message}`);
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        
        const icon = type === 'success' ? '✅' : '❌';
        toast.innerHTML = `<span class="toast-icon">${icon}</span> ${message}`;

        this.container.appendChild(toast);

        // Force reflow to enable the CSS transition
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Set a timeout to remove the toast
        setTimeout(() => {
            toast.classList.remove('show');
            // Remove the element from the DOM after the transition ends
            toast.addEventListener('transitionend', () => {
                if (toast.parentElement) {
                    toast.remove();
                }
            });
        }, 3000); // The toast will disappear after 3 seconds
    }
}

// Export a singleton instance so the whole app uses the same service
export const NotificationService = new NotificationServiceController();