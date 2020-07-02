import React from 'react';
import { render, wait } from '@testing-library/react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../theme';
import { StatusBox } from './StatusBox';
import { programStatusToColor } from '../../utils/utils';

const statusData = {
  status: 'ACTIVE',
  function: programStatusToColor
}

describe('Status box', () => {
  test('StatusBox to contain given text', () => {
    const { container } = render(
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <StatusBox status={statusData.status} statusToColor={statusData.function} />
        </StyledThemeProvider>
      </ThemeProvider>
    )
    wait(() => expect(container).toHaveTextContent(statusData.status));
  })
})