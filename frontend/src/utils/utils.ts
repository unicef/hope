import { theme as themeObj } from '../theme';

export function opacityToHex(opacity: number): string {
  return Math.floor(opacity * 0xff).toString(16);
}

export function programStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'ACTIVE':
      return theme.hctPalette.green;
    case 'FINISHED':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.oragne;
  }
}
