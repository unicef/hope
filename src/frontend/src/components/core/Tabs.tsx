import { Tab as MuiTab, Tabs as MuiTabs, styled } from '@mui/material';
import type { TabsProps } from '@mui/material';
import type { ReactElement } from 'react';
import { useIsMobile } from 'src/responsive';

export const Tab = styled(MuiTab)({
  '&.Mui-selected': {
    outline: 'none',
  },
  '&:focus': {
    outline: 'none',
  },
  '&:focus-visible': {
    outline: 'none',
  },
});

const StyledTabs = styled(MuiTabs)({
  '&.Mui-selected': {
    outline: 'none',
  },
  '&:focus': {
    outline: 'none',
  },
  '&:focus-visible': {
    outline: 'none',
  },
});

/** Scrolls sideways on mobile, where the tab labels rarely fit in one row. */
export function Tabs(props: TabsProps): ReactElement {
  const isMobile = useIsMobile();
  return (
    <StyledTabs variant={isMobile ? 'scrollable' : undefined} {...props} />
  );
}
