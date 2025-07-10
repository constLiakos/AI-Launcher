// src/renderer/components/Settings/ApiSettingsTab.ts

import { LLMProvider, LLMProviderType, Model } from "@shared/types";
import { AppConfig } from "@shared/config/AppConfig";
import { NotificationService } from "@renderer/services/NotificationService";
import { ConfirmationModal } from "@renderer/services/ConfirmationService";


function escapeHTML(str: string | null | undefined): string {
    if (!str) return '';
    const p = document.createElement("p");
    p.textContent = str;
    return p.innerHTML;
}

export const APISettingsTab = {
    render(container: HTMLElement, config: AppConfig): void {

        container.innerHTML = `
            <div class="settings-section">
                <h3>Default Chat Model</h3>
                <p>Select the default model. This will also set the default provider.</p>
                <div class="form-group">
                    <label for="default-chat-model-select">Default Model</label>
                    <select id="default-chat-model-select" class="settings-input"></select>
                </div>
            </div>

            <div class="settings-section">
                <h3>Configured Providers</h3>
                <p>The provider with the star (<i class="fas fa-star is-default"></i>) is the current default.</p>
                <ul class="provider-list"></ul>
                <button id="add-provider-btn" class="btn btn-primary">Add New Provider</button>
            </div>

            <!-- Provider Edit/Add Modal -->
            <div id="provider-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content">
                    <form id="provider-form">
                        <h4 id="modal-title">Add New Provider</h4>
                        <input type="hidden" id="editing-provider-id">
                        <div class="form-group">
                            <label for="provider-name-input">Connection Name</label>
                            <input type="text" id="provider-name-input" placeholder="e.g., My OpenAI Key" required>
                        </div>
                        <div class="form-group">
                            <label for="provider-type-select">Provider Type</label>
                            <select id="provider-type-select" required>
                                ${Object.values(LLMProviderType).map(type => `<option value="${type}">${type.toUpperCase()}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="provider-apiKey-input">API Key</label>
                            <input type="password" id="provider-apiKey-input" placeholder="sk-...">
                        </div>
                        <div class="form-group">
                            <label for="provider-apiBase-input">API Base URL (Optional)</label>
                            <input type="text" id="provider-apiBase-input" placeholder="e.g., https://api.openai.com/v1">
                        </div>
                        <div class="form-group">
                            <label for="provider-model-select">Model List</label>
                            <div class="model-select-wrapper">
                                <select id="provider-model-select"></select>
                                <button type="button" id="refresh-models-btn" class="icon-button" title="Refresh Models"><i class="fas fa-sync-alt"></i></button>
                            </div>
                            <p class="description">Select a model. Type a custom name and press Enter to add.</p>
                        </div>
                        <div class="modal-actions">
                            <button type="button" class="btn btn-secondary" data-action="cancel-modal">Cancel</button>
                            <button type="submit" class="btn btn-primary" data-action="save-modal">Save Provider</button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- NEW: Confirmation Modal for Deletion -->
            <div id="confirm-delete-modal" class="modal-overlay" style="display: none;">
                <div class="modal-content small-modal">
                    <h4>Confirm Deletion</h4>
                    <p id="confirm-delete-message">Are you sure you want to delete this provider?</p>
                    <div class="modal-actions">
                        <button type="button" class="btn btn-secondary" id="cancel-delete-btn">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirm-delete-btn">Delete</button>
                    </div>
                </div>
            </div>
        `;

        const providerListEl = container.querySelector('.provider-list') as HTMLElement;
        this._renderProviderList(providerListEl, config.providers, config.defaultProviderId);
        this._populateAllModelsDropdown(container, config);
        this._bindEvents(container);
        this._updateStarBasedOnDefaultModel(container);
    },

    getFormData(container: HTMLElement): Partial<AppConfig> {
        const providerItems = container.querySelectorAll<HTMLElement>('.provider-item');
        const providers: LLMProvider[] = [];
        providerItems.forEach(item => {
            providers.push(this._getProviderDataFromListItem(item));
        });

        const defaultChatModelSelect = container.querySelector('#default-chat-model-select') as HTMLSelectElement;
        const defaultChatModelId = defaultChatModelSelect.value;

        let defaultProviderId: string | null = null;
        if (defaultChatModelId) {
            const selectedOption = defaultChatModelSelect.options[defaultChatModelSelect.selectedIndex];
            if (selectedOption) {
                defaultProviderId = selectedOption.dataset.providerId || null;
            }
        }
        if (!defaultProviderId && providers.length > 0) {
            defaultProviderId = providers[0].id;
        }

        return { providers, defaultProviderId, defaultChatModelId };
    },

    _renderProviderList(listElement: HTMLElement, providers: LLMProvider[] | undefined, defaultProviderId: string | null): void {
        listElement.innerHTML = '';
        if (!providers || providers.length === 0) {
            listElement.innerHTML = `<li class="empty-state">No providers configured.</li>`;
            return;
        }
        providers.forEach(p => {
            const li = this._createProviderItemElement(p, false, providers.length);
            listElement.appendChild(li);
        });
    },

    _createProviderItemElement(provider: LLMProvider, isDefault: boolean, providerCount: number): HTMLElement {
        const li = document.createElement('li');
        li.className = 'provider-item';
        this._updateProviderDataOnListItem(li, provider);
        li.innerHTML = `
            <div class="provider-info">
                <span class="provider-name">${escapeHTML(provider.name)}</span>
                <span class="provider-type">${escapeHTML(provider.type)}</span>
            </div>
            <div class="provider-actions">
                 <button class="icon-button set-default-btn" title="Default Provider" disabled>
                    <i class="fas fa-star"></i>
                </button>
                <button class="btn btn-secondary" data-action="edit-provider">Edit</button>
                <button class="btn btn-danger" data-action="delete-provider" ${providerCount <= 1 ? 'disabled' : ''}>Delete</button>
            </div>
        `;
        return li;
    },

    _bindEvents(container: HTMLElement): void {
        const modal = container.querySelector('#provider-modal') as HTMLElement;
        const form = container.querySelector('#provider-form') as HTMLFormElement;

        container.querySelector('.provider-list')?.addEventListener('click', async (e) => {
            const button = (e.target as HTMLElement).closest('button[data-action]');
            if (!button || (button as HTMLButtonElement).disabled) return;

            const action = button.dataset.action;
            const li = button.closest('.provider-item') as HTMLElement;
            if (!li) return;

            if (action === 'edit-provider') {
                this._openModal(container, li);
                return;
            }

            if (action === 'delete-provider') {
                try {
                    await ConfirmationModal.show({
                        title: 'Confirm Deletion',
                        message: `Are you sure you want to delete "${li.dataset.name}"?`,
                        confirmText: 'Delete',
                        cancelText: 'Cancel'
                    });

                    li.remove();
                    this._updateAfterProviderChange(container);
                    NotificationService.showSuccess('Provider deleted successfully.');

                } catch (error) {
                    if (error) {
                        console.error('Could not delete provider: ', error);
                        NotificationService.showError(`Could not delete provider: ${error}`);
                    } else {
                        console.log('Deletion was cancelled by the user.');
                    }
                }
            }
        });

        container.querySelector('#default-chat-model-select')?.addEventListener('change', () => {
            this._updateStarBasedOnDefaultModel(container);
            container.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
        });

        container.querySelector('#add-provider-btn')?.addEventListener('click', () => this._openModal(container, null));
        form.addEventListener('submit', e => { e.preventDefault(); this._handleFormSave(container); });
        modal.querySelector('[data-action="cancel-modal"]')?.addEventListener('click', () => this._closeModal(container));
        modal.querySelector('#refresh-models-btn')?.addEventListener('click', async () => {
            const freshModels = await this._fetchModelsFromAPI(form);
            const customModels = this._getCustomModelsFromSelect(form.querySelector('#provider-model-select'));
            this._populateModelsInModal(form, freshModels, customModels);
        });
    },




    _updateStarBasedOnDefaultModel(container: HTMLElement): void {
        const select = container.querySelector('#default-chat-model-select') as HTMLSelectElement;
        const selectedOption = select.options[select.selectedIndex];
        const providerId = selectedOption?.dataset.providerId;

        container.querySelectorAll('.set-default-btn').forEach(btn => {
            btn.classList.remove('is-default');
        });

        if (providerId) {
            const providerItem = container.querySelector(`.provider-item[data-id="${providerId}"]`);
            providerItem?.querySelector('.set-default-btn')?.classList.add('is-default');
        }
    },
    _populateAllModelsDropdown(container: HTMLElement, config: AppConfig): void {
        const select = container.querySelector('#default-chat-model-select') as HTMLSelectElement;
        const currentSelectedValue = select.value;
        select.innerHTML = '';

        if (!config.providers || config.providers.length === 0) {
            select.innerHTML = '<option>No providers configured</option>';
            return;
        }

        config.providers.forEach(provider => {
            const optGroup = document.createElement('optgroup');
            optGroup.label = escapeHTML(provider.name);

            const modelIdSet = new Set<string>();
            const allProviderModels = [...(provider.availableModels || []), ...(provider.customModels || [])];

            allProviderModels.forEach(model => {
                if (!modelIdSet.has(model.id)) {
                    const opt = new Option(model.name, model.id);
                    opt.dataset.providerId = provider.id;
                    optGroup.appendChild(opt);
                    modelIdSet.add(model.id);
                }
            });

            if (optGroup.hasChildNodes()) {
                select.appendChild(optGroup);
            }
        });

        const validValue = [currentSelectedValue, config.defaultChatModelId].find(v => v && select.querySelector(`option[value="${CSS.escape(v)}"]`));
        select.value = validValue || (select.options.length > 0 ? select.options[0].value : '');
    },

    _openModal(container: HTMLElement, li: HTMLElement | null): void {
        const modal = container.querySelector('#provider-modal') as HTMLElement;
        const form = container.querySelector('#provider-form') as HTMLFormElement;
        const title = modal.querySelector('#modal-title') as HTMLElement;

        form.reset();

        const providerData = li ? this._getProviderDataFromListItem(li) : this._getDefaultProviderData();

        title.textContent = li ? 'Edit Provider' : 'Add New Provider';
        (form.querySelector('#editing-provider-id') as HTMLInputElement).value = providerData.id || '';
        (form.querySelector('#provider-name-input') as HTMLInputElement).value = providerData.name || '';
        (form.querySelector('#provider-type-select') as HTMLSelectElement).value = providerData.type;
        (form.querySelector('#provider-apiKey-input') as HTMLInputElement).value = providerData.apiKey || '';
        (form.querySelector('#provider-apiBase-input') as HTMLInputElement).value = providerData.apiBase || '';

        this._populateModelsInModal(form, providerData.availableModels ?? [], providerData.customModels ?? [], undefined);

        modal.style.display = 'flex';
    },

    _closeModal(container: HTMLElement): void {
        (container.querySelector('#provider-modal') as HTMLElement).style.display = 'none';
    },

    _handleFormSave(container: HTMLElement): void {
        const form = container.querySelector('#provider-form') as HTMLFormElement;
        const id = (form.querySelector('#editing-provider-id') as HTMLInputElement).value;
        const modelSelect = form.querySelector('#provider-model-select') as HTMLSelectElement;

        const availableModels: Model[] = [];
        const customModels: Model[] = [];
        Array.from(modelSelect.options).forEach(opt => {
            const model: Model = { id: opt.value, name: opt.text, providerType: (form.querySelector('#provider-type-select') as HTMLSelectElement).value as LLMProviderType, providerId: id };
            if (opt.dataset.isCustom === 'true') customModels.push(model);
            else availableModels.push(model);
        });

        const providerData: LLMProvider = {
            ...this._getDefaultProviderData(),
            id: id || `new_${Date.now()}`,
            name: (form.querySelector('#provider-name-input') as HTMLInputElement).value,
            type: (form.querySelector('#provider-type-select') as HTMLSelectElement).value as LLMProviderType,
            apiKey: (form.querySelector('#provider-apiKey-input') as HTMLInputElement).value,
            apiBase: (form.querySelector('#provider-apiBase-input') as HTMLInputElement).value,
            availableModels,
            customModels
        };
        if (!id) providerData.customModels?.forEach(m => m.providerId = providerData.id);

        let li = id ? container.querySelector(`.provider-item[data-id="${id}"]`) as HTMLElement : null;
        const list = container.querySelector('.provider-list') as HTMLElement;

        if (li) {
            this._updateProviderDataOnListItem(li, providerData);
            li.querySelector('.provider-name')!.textContent = providerData.name;
        } else {
            const isFirstItem = list.children.length === 0;
            li = this._createProviderItemElement(providerData, isFirstItem, list.children.length + 1);
            list.appendChild(li);
        }

        this._updateAfterProviderChange(container);
        this._closeModal(container);
    },

    _updateAfterProviderChange(container: HTMLElement): void {
        const config = this.getFormData(container);
        this._populateAllModelsDropdown(container, config as AppConfig);
        this._updateStarBasedOnDefaultModel(container);
        this._updateDeleteButtonsState(container);
        container.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
    },

    _updateDeleteButtonsState(container: HTMLElement): void {
        const deleteButtons = container.querySelectorAll<HTMLButtonElement>('[data-action="delete-provider"]');
        const disable = deleteButtons.length <= 1;
        deleteButtons.forEach(btn => btn.disabled = disable);
    },

    _updateProviderDataOnListItem(li: HTMLElement, provider: Omit<LLMProvider, 'model'>): void {
        Object.entries(provider).forEach(([key, value]) => {
            li.dataset[key.toLowerCase()] = (typeof value === 'object' && value != null) ? JSON.stringify(value) : String(value ?? '');
        });
    },

    _getProviderDataFromListItem(li: HTMLElement): LLMProvider {
        const ds = li.dataset;
        return {
            id: ds.id!, name: ds.name!, type: ds.type! as LLMProviderType,
            apiKey: ds.apikey!, apiBase: ds.apibase!,
            timeout: parseInt(ds.timeout || '120000'),
            temperature: parseFloat(ds.temperature || '0.7'),
            maxTokens: parseInt(ds.maxtokens || '4096'),
            systemPrompt: ds.systemprompt!,
            availableModels: ds.availablemodels ? JSON.parse(ds.availablemodels) : [],
            customModels: ds.custommodels ? JSON.parse(ds.custommodels) : [],
        };
    },

    _getDefaultProviderData(): Omit<LLMProvider, 'model'> {
        return {
            id: '', name: '', type: LLMProviderType.OPENAI, apiKey: '', apiBase: '',
            timeout: 120000, temperature: 0.7, maxTokens: 4096, systemPrompt: 'You are a helpful assistant.',
            availableModels: [], customModels: []
        };
    },

    _getCustomModelsFromSelect(select: HTMLSelectElement | null): Model[] {
        if (!select) return [];
        return Array.from(select.options)
            .filter(opt => opt.dataset.isCustom === 'true')
            .map(opt => ({ id: opt.value, name: opt.text, providerType: LLMProviderType.OPENAI, providerId: '' }));
    },
    async _fetchModelsFromAPI(form: HTMLFormElement): Promise<Model[]> {
        const modelSelect = form.querySelector('#provider-model-select') as HTMLSelectElement;
        const originalText = modelSelect.options[0]?.text || 'Click Refresh to load';
        modelSelect.innerHTML = '<option>Loading...</option>';
        modelSelect.disabled = true;

        const providerForFetch: Partial<LLMProvider> = {
            type: (form.querySelector('#provider-type-select') as HTMLSelectElement).value as LLMProviderType,
            apiKey: (form.querySelector('#provider-apiKey-input') as HTMLInputElement).value,
            apiBase: (form.querySelector('#provider-apiBase-input') as HTMLInputElement).value,
        };
        const response = await window.electronAPI.fetchAvailableModels(providerForFetch as LLMProvider);
        
        modelSelect.disabled = false;
        if (response.success && response.data) {
            return response.data.sort((a, b) => a.id.localeCompare(b.id, undefined, { sensitivity: 'base' }));
        }
        
        NotificationService.showError(`Failed to fetch models: ${response.error || 'Unknown error'}`);
        modelSelect.innerHTML = `<option>${originalText}</option>`;
        return [];
    },

    _populateModelsInModal(form: HTMLFormElement, available: Model[], custom: Model[], selectedId?: string): void {
        const modelSelect = form.querySelector('#provider-model-select') as HTMLSelectElement;
        modelSelect.innerHTML = '';

        const allModels = new Map<string, { model: Model, isCustom: boolean }>();
        available.forEach(m => allModels.set(m.id, { model: m, isCustom: false }));
        custom.forEach(m => allModels.set(m.id, { model: m, isCustom: true }));

        if (allModels.size === 0) {
            modelSelect.innerHTML = '<option value="">Click Refresh to load models</option>';
        } else {
            allModels.forEach(({ model, isCustom }) => {
                const option = new Option(model.name, model.id, false, model.id === selectedId);
                if (isCustom) option.dataset.isCustom = 'true';
                modelSelect.add(option);
            });
        }
    }
};