import { AppConfig } from '@shared/config/AppConfig';
import { ThemeType } from '@shared/constants/themes';

export const GeneralSettingsTab = {
  render: (container: HTMLElement, config: AppConfig): void => {
    const themeOptionsHtml = Object.values(ThemeType).map(theme => {
      return `<option value="${theme}">${theme}</option>`;
    }).join('');

    container.innerHTML = `
      <div class="settings-form-container">
        <h3 class="form-title">General Settings</h3>
        <p class="form-description">
          Configure general application behavior.
        </p>
        <div class="form-group">
          <label for="theme-select">Theme</label>
          <select id="theme-select" name="theme">
            ${themeOptionsHtml}
          </select>
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" name="preferences.autostart">
            Launch AI Launcher on system startup
          </label>
        </div>
      </div>
    `;

    const themeSelect = container.querySelector<HTMLSelectElement>('#theme-select');
    if (themeSelect) {
      themeSelect.value = config.theme || ThemeType.CLASSIC;
    }

    const autostartCheckbox = container.querySelector<HTMLInputElement>('input[name="preferences.autostart"]');
    if (autostartCheckbox) {
      autostartCheckbox.checked = config.preferences?.autostart ?? false;
    }
  },

  getFormData: (container: HTMLElement): Partial<AppConfig> => {
    const themeSelect = container.querySelector<HTMLSelectElement>('#theme-select');
    const autostartCheckbox = container.querySelector<HTMLInputElement>('input[name="preferences.autostart"]');
    
    const preferences = {
        autostart: autostartCheckbox?.checked ?? false,
    };

    return {
      theme: themeSelect?.value as ThemeType,
      preferences: preferences as any,
    };
  }
};