export * from '@shared/constants/window';
export * from '@shared/constants/ui';
export * from '@shared/constants/animations';
export * from '@shared/constants/text';
export * from '@shared/constants/hotkeys';
export * from '@shared/constants/themes';
export * from '@shared/constants/timing';
export { TIMING, getRetryDelay, getRandomDelay, getAIResponseDelay } from './timing';
// export * from '@shared/constants/paths';
// export * from '@shared/constants/api';


export { UI_SIZES, COLORS } from './ui';
export { ANIMATION_DURATIONS, EASING_CURVES } from './animations';

// Export commonly used items
// Export ONLY theme data/types, NOT the manager
export {
  ThemeType,
  type ThemeColors,
  getLightTheme,
  getDarkTheme,
  getNatureTheme,
  getRoseTheme,
  getHuaweiTheme,
} from './themes';

// Export window utilities
export {
  getWindowSize,
  getCenterPosition,
  validateDimensions,
  validatePosition
} from './window';