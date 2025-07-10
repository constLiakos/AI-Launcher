// src/renderer/components/Settings/SttSettingsTab.ts

import { AppConfig } from "@shared/config/AppConfig";
import { STTProviderType } from "@shared/types";

function escapeHTML(str: string | null | undefined): string {
    if (!str) return '';
    const p = document.createElement("p");
    p.textContent = str;
    return p.innerHTML;
}

export const SttSettingsTab = {
    render(container: HTMLElement, config: AppConfig): void {
        const sttConfig = config.stt;
        container.innerHTML = `
            <div class="settings-section">
                <h3>Speech-to-Text (STT) Settings</h3>
                <p>Configure the service used for voice transcription.</p>

                <div class="form-group">
                    <label for="stt-enabled-toggle">Enable STT</label>
                    <label class="switch">
                        <input type="checkbox" id="stt-enabled-toggle" ${sttConfig.enabled ? 'checked' : ''}>
                        <span class="slider round"></span>
                    </label>
                </div>

                <div id="stt-settings-fields" class="${sttConfig.enabled ? '' : 'disabled'}">
                    <div class="form-group">
                        <label for="stt-provider-select">STT Provider</label>
                        <select id="stt-provider-select" class="settings-input">
                            ${Object.values(STTProviderType).map(type =>
                                `<option value="${type}" ${sttConfig.provider === type ? 'selected' : ''}>${type.toUpperCase()}</option>`
                            ).join('')}
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="stt-api-key-input">API Key</label>
                        <input type="password" id="stt-api-key-input" class="settings-input" placeholder="Enter your API key" value="${escapeHTML(sttConfig.apiKey)}">
                    </div>
                    
                    <div class="form-group">
                        <label for="stt-api-base-input">API Base URL</label>
                        <input type="text" id="stt-api-base-input" class="settings-input" placeholder="e.g., https://api.openai.com/v1" value="${escapeHTML(sttConfig.apiBase)}">
                    </div>

                    <div class="form-group">
                        <label for="stt-model-input">Model Name</label>
                        <input type="text" id="stt-model-input" class="settings-input" placeholder="e.g., whisper-1" value="${escapeHTML(sttConfig.model)}">
                    </div>
                </div>
            </div>
        `;

        this._bindEvents(container);
    },

    getFormData(container: HTMLElement): { stt: Partial<AppConfig['stt']> } {
        const enabled = (container.querySelector('#stt-enabled-toggle') as HTMLInputElement).checked;
        const provider = (container.querySelector('#stt-provider-select') as HTMLSelectElement).value as STTProviderType;
        const apiKey = (container.querySelector('#stt-api-key-input') as HTMLInputElement).value;
        const apiBase = (container.querySelector('#stt-api-base-input') as HTMLInputElement).value;
        const model = (container.querySelector('#stt-model-input') as HTMLInputElement).value;

        // Retrieve the existing timeout from the config to avoid overwriting it
        // const currentTimeout = (window as any).electronAPI ? (window as any).electronAPI.loadConfig().stt.timeout : 15000;

        return {
            stt: {
                enabled,
                provider,
                apiKey,
                apiBase,
                model,
                // timeout: currentTimeout, // Preserve existing timeout
            }
        };
    },

    _bindEvents(container: HTMLElement): void {
        const enabledToggle = container.querySelector('#stt-enabled-toggle') as HTMLInputElement;
        const settingsFields = container.querySelector('#stt-settings-fields') as HTMLElement;

        enabledToggle.addEventListener('change', () => {
            if (enabledToggle.checked) {
                settingsFields.classList.remove('disabled');
            } else {
                settingsFields.classList.add('disabled');
            }
            // Trigger change detection
            container.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
        });
    }
};
