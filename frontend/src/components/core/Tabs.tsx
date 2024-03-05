import { Tab as MuiTab, Tabs as MuiTabs, styled } from '@mui/material';

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

export const Tabs = styled(MuiTabs)({
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
