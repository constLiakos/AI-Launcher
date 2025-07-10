// src/shared/constants/timing.ts
export const TIMING = {
  // API Response delays
  AI_RESPONSE_DELAY: 1000,
  AI_RESPONSE_DELAY_MIN: 500,
  AI_RESPONSE_DELAY_MAX: 2000,
  
  // UI Feedback delays  
  NOTIFICATION_DURATION: 3000,
  TOOLTIP_DELAY: 500,
  MODAL_CLOSE_DELAY: 300,
  THEME_CHANGE_DELAY: 300,
  
  // Debounce timers
  WINDOW_SAVE_DEBOUNCE: 1000,
  SEARCH_DEBOUNCE: 300,
  INPUT_VALIDATION_DEBOUNCE: 500,
  
  // Animation durations (extend existing)
  FADE_IN: 300,
  SLIDE_IN: 250,
  BOUNCE_IN: 400,
  
  // Retry intervals
  RETRY_DELAY_BASE: 1000,
  RETRY_DELAY_MAX: 10000,
  RETRY_ATTEMPTS: 3,
  
  // Polling intervals
  HEALTH_CHECK_INTERVAL: 30000,
  CONFIG_WATCH_INTERVAL: 1000,
  
  // Timeouts
  IPC_TIMEOUT: 5000,
  WINDOW_FOCUS_TIMEOUT: 100,
  STARTUP_TIMEOUT: 10000
} as const;

// Helper functions for dynamic timing
export const getRetryDelay = (attempt: number): number => {
  return Math.min(
    TIMING.RETRY_DELAY_BASE * Math.pow(2, attempt),
    TIMING.RETRY_DELAY_MAX
  );
};

export const getRandomDelay = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

export const getAIResponseDelay = (): number => {
  return getRandomDelay(TIMING.AI_RESPONSE_DELAY_MIN, TIMING.AI_RESPONSE_DELAY_MAX);
};