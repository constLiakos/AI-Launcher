import {
    ThemeType,
    ThemeColors,
    getLightTheme,
    getDarkTheme,
    getNatureTheme,
    getRoseTheme,
    getHuaweiTheme
} from '@shared/constants/themes';


export class ThemeManager {
    private static instance: ThemeManager;
    private currentTheme: ThemeType = ThemeType.CLASSIC;
    private themes: Record<ThemeType, ThemeColors>;
    private listeners: Array<(theme: ThemeType) => void> = [];


    private constructor() {
        this.themes = {
            [ThemeType.CLASSIC]: getLightTheme(),
            [ThemeType.DARK]: getDarkTheme(),
            [ThemeType.NATURE]: getNatureTheme(),
            [ThemeType.ROSE]: getRoseTheme(),
            [ThemeType.HUAWEI]: getHuaweiTheme()
        };
    }

    addListener(callback: (theme: ThemeType) => void): void {
        this.listeners.push(callback);
    }

    static getInstance(): ThemeManager {
        if (!ThemeManager.instance) {
            ThemeManager.instance = new ThemeManager();
        }
        return ThemeManager.instance;
    }

    getAllThemes(): Record<ThemeType, ThemeColors> {
        return this.themes;
    }

    getTheme(themeType: ThemeType): ThemeColors {
        return this.themes[themeType];
    }

    getCurrentTheme(): ThemeColors {
        return this.themes[this.currentTheme];
    }

    getCurrentThemeType(): ThemeType {
        return this.currentTheme;
    }

    setTheme(themeType: ThemeType): void {
        this.currentTheme = themeType;
        this.applyThemeToDOM();
    }

    private applyThemeToDOM(): void {
        if (typeof document === 'undefined') return;

        const theme = this.getCurrentTheme();
        const root = document.documentElement;

        // Apply all theme colors as CSS custom properties
        Object.entries(theme).forEach(([key, value]) => {
            root.style.setProperty(`--${key.replace(/_/g, '-')}`, value);
        });

        // Set theme class on body for additional styling
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        document.body.classList.add(`theme-${this.currentTheme.toLowerCase()}`);
    }

    getCSSVariables(): Record<string, string> {
        const theme = this.getCurrentTheme();
        const cssVars: Record<string, string> = {};

        Object.entries(theme).forEach(([key, value]) => {
            cssVars[`--${key.replace(/_/g, '-')}`] = value;
        });

        return cssVars;
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

export const getThemeColors = (themeType: ThemeType): ThemeColors => {
    return ThemeManager.getInstance().getTheme(themeType);
};

export const getCurrentTheme = (): ThemeColors => {
    return ThemeManager.getInstance().getCurrentTheme();
};

export const setTheme = (themeType: ThemeType): void => {
    ThemeManager.getInstance().setTheme(themeType);
};

export const getAllThemes = (): Record<ThemeType, ThemeColors> => {
    return ThemeManager.getInstance().getAllThemes();
};

// Default export
export default ThemeManager;

