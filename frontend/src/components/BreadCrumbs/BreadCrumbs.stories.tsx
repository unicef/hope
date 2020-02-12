import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../theme';
import { BreadCrumbs } from './BreadCrumbs';
import { StoryRouter } from '../../../.storybook/StoryRouter';

export default {
  component: BreadCrumbs,
  title: 'BreadCrumbs',
};

const propsData = [
  { title: 'Programme Management', to: '/first-url' },
  { title: 'Cash Plan', to: '/second-url' },
  { title: 'Payment Record', to: '/third-url' },
];

export const ProgramStatuses = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <StoryRouter>
          <BreadCrumbs breadCrumbs={propsData} />
        </StoryRouter>
      </StyledThemeProvider>
    </ThemeProvider>
  );
};
