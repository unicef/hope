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


export function cashPlanStatusToColor(
  theme: typeof themeObj,
  status: string,
): string {
  switch (status) {
    case 'STARTED':
      return theme.hctPalette.green;
    case 'COMPLETE':
      return theme.hctPalette.gray;
    default:
      return theme.hctPalette.oragne;
  }
}
export function paymentRecordStatusToColor(
         theme: typeof themeObj,
         status: string,
       ): string {
         switch (status) {
           case 'SUCCESS':
             return theme.hctPalette.green;
           case 'PENDING':
             return theme.hctPalette.oragne;
           default:
             return theme.palette.error.main;
         }
       }
export function getCookie(name): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2)
    return parts
      .pop()
      .split(';')
      .shift();
  return null;
}
export function getCurrentLocation(): string {
  return localStorage.getItem('LocationId');
}
export function isAuthenticated(): boolean {
  return Boolean(localStorage.getItem('AUTHENTICATED'));
}
export function setAuthenticated(authenticated: boolean): void {
  localStorage.setItem('AUTHENTICATED', `${authenticated}`);
}

export function selectFields(
  fullObject,
  keys: string[],
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): { [key: string]: any } {
  return keys.reduce((acc, current) => {
    acc[current] = fullObject[current];
    return acc;
  }, {});
}

export function camelToUnderscore(key): string {
  return key.replace(/([A-Z])/g, '_$1').toLowerCase();
}

export function columnToOrderBy(
  column: string,
  orderDirection: string,
): string {
  return camelToUnderscore(`${orderDirection === 'desc' ? '-' : ''}${column}`);
}
