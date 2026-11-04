import { responsiveValue } from './breakpoints';

/**
 * `sx` for `TablePagination`: on mobile the toolbar wraps onto two lines so
 * the page arrows stay on screen. Desktop keeps the MUI defaults.
 */
export const PAGINATION_SX = {
  '.MuiTablePagination-toolbar': {
    flexWrap: responsiveValue('wrap', 'nowrap'),
    justifyContent: 'flex-end',
    rowGap: responsiveValue(1, 0),
  },
  '.MuiTablePagination-spacer': {
    display: responsiveValue('none', 'block'),
  },
};
