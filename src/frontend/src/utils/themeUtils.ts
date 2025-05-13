import theme from '../theme';

/**
 * Gets a color from the theme's hctPalette with type safety
 * @param colorName The name of the color in hctPalette
 * @returns The color value
 */
export const getThemeColor = (colorName: keyof typeof theme.hctPalette): string => {
  return theme.hctPalette[colorName];
};