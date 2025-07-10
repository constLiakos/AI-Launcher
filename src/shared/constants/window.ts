// =============================================================================
// WINDOW DIMENSIONS & CONFIGURATIONS
// =============================================================================
import { InputMode, WindowState } from "@shared/types";
const HISTORY_SIDEBAR_WIDTH = 250;

export const WINDOW_SIZE = {
  // Base widths
  COMPACT_WIDTH: 650,
  EXPANDED_WIDTH: 650,

  // Fallback and minimum heights
  COMPACT_HEIGHT: 130, // Fallback height for compact mode
  MIN_EXPANDED_HEIGHT: 550, // Minimum height when expanded
  CHAT_AREA_BASE_HEIGHT: 320, // Base height for the chat/response area
  SCREEN_SOURCE_PICKER_HEIGHT: 450,

  // Constraints
  MIN_WIDTH: 400,
  MIN_HEIGHT: 100,
  MAX_WIDTH: 1200,
  MAX_HEIGHT: 1000
} as const

export const WINDOW_CONFIG = {
  // Default window options
  DEFAULT: {
    show: false,
    frame: false,
    transparent: true,
    alwaysOnTop: false,
    skipTaskbar: false,
    resizable: true,
    maximizable: false,
    minimizable: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
      webSecurity: true,
      allowRunningInsecureContent: false,
      experimentalFeatures: false
    }
  },
  
  // Development-specific options
  DEVELOPMENT: {
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
      webSecurity: false, // Disabled for dev server
      allowRunningInsecureContent: true,
      experimentalFeatures: true
    }
  },
  
  // Production options
  PRODUCTION: {
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true, // Enable sandbox in production
      webSecurity: true,
      allowRunningInsecureContent: false,
      experimentalFeatures: false
    }
  },
  
  // Window behavior
  BEHAVIOR: {
    centerOnCreate: true,
    hideOnBlur: false,
    restorePosition: true,
    rememberSize: true
  }
} as const;

export const WINDOW_STATES = {
  COMPACT: 'compact',
  EXPANDED: 'expanded',
  HIDDEN: 'hidden',
  MINIMIZED: 'minimized'
} as const;

// =============================================================================
// RESPONSIVE BREAKPOINTS
// =============================================================================

export const BREAKPOINTS = {
  SMALL: 480,
  MEDIUM: 768,
  LARGE: 1024,
  XLARGE: 1200
} as const;

// =============================================================================
// WINDOW POSITIONING
// =============================================================================

export const POSITIONING = {
  CENTER: 'center',
  TOP_LEFT: 'top-left',
  TOP_RIGHT: 'top-right',
  BOTTOM_LEFT: 'bottom-left',
  BOTTOM_RIGHT: 'bottom-right',
  REMEMBER_POSITION: 'remember'
} as const;

// =============================================================================
// WINDOW ANIMATIONS
// =============================================================================

export const WINDOW_ANIMATIONS = {
  SHOW_DURATION: 200,
  HIDE_DURATION: 150,
  RESIZE_DURATION: 300,
  FADE_DURATION: 250
} as const;

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Get appropriate web preferences based on environment
 */
export function getWebPreferences(isDev: boolean, preloadPath?: string) {
  const basePreferences = isDev 
    ? WINDOW_CONFIG.DEVELOPMENT.webPreferences 
    : WINDOW_CONFIG.PRODUCTION.webPreferences;

  return {
    ...basePreferences,
    ...(preloadPath && { preload: preloadPath })
  };
}

/**
 * Get window size for specific state and input mode
 */
// const dimensions = getWindowSize(baseState, this.inputArea.getInputMode(), input_area_heights.input_area, this.isHistoryVisible);

export function getWindowSize(
  state: WindowState.COMPACT | WindowState.EXPANDED,
  inputAreaHeight: number | null,
  isHistoryVisible: boolean | null
): { width: number; height: number } {
  let width: number
  let height: number

  if (state === WindowState.COMPACT) {
    // In compact mode, width is fixed, and height is determined by the input area.
    width = WINDOW_SIZE.COMPACT_WIDTH
    height = inputAreaHeight ?? WINDOW_SIZE.COMPACT_HEIGHT
  } else {
    // In expanded mode, width is fixed, and height is dynamic.
    width = WINDOW_SIZE.EXPANDED_WIDTH

    // The total height is the sum of the chat area and the input area.
    // If inputAreaHeight is not provided, use a small fallback (e.g., 50px).
    const dynamicHeight = WINDOW_SIZE.CHAT_AREA_BASE_HEIGHT + (inputAreaHeight ?? 50)

    // Ensure the height is not less than the minimum defined for expanded mode.
    height = Math.max(WINDOW_SIZE.MIN_EXPANDED_HEIGHT, dynamicHeight)
  }

  // If the history sidebar is visible, add its width to the total width.
  if (isHistoryVisible) {
    width += HISTORY_SIDEBAR_WIDTH
  }

  return { width, height }
}

/**
 * Calculate center position for window
 */
export function getCenterPosition(
  windowWidth: number,
  windowHeight: number,
  screenWidth: number,
  screenHeight: number
): { x: number; y: number } {
  return {
    x: Math.round((screenWidth - windowWidth) / 2),
    y: Math.round((screenHeight - windowHeight) / 2)
  };
}

/**
 * Validate window dimensions
 */
export function validateDimensions(
  width: number,
  height: number
): { isValid: boolean; adjustedWidth: number; adjustedHeight: number } {
  const adjustedWidth = Math.max(
    WINDOW_SIZE.MIN_WIDTH,
    Math.min(WINDOW_SIZE.MAX_WIDTH, width)
  );
  
  const adjustedHeight = Math.max(
    WINDOW_SIZE.MIN_HEIGHT,
    Math.min(WINDOW_SIZE.MAX_HEIGHT, height)
  );
  
  return {
    isValid: adjustedWidth === width && adjustedHeight === height,
    adjustedWidth,
    adjustedHeight
  };
}

/**
 * Validate window position
 */
export function validatePosition(
  x: number,
  y: number,
  width: number,
  height: number,
  screenWidth: number,
  screenHeight: number
): { isValid: boolean; adjustedX: number; adjustedY: number } {
  const maxX = screenWidth - width;
  const maxY = screenHeight - height;
  
  const adjustedX = Math.max(0, Math.min(maxX, x));
  const adjustedY = Math.max(0, Math.min(maxY, y));
  
  return {
    isValid: adjustedX === x && adjustedY === y,
    adjustedX,
    adjustedY
  };
}

