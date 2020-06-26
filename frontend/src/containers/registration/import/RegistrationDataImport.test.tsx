import React from 'react';
import { render, fireEvent, wait, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MockedProvider } from '@apollo/react-testing';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../../theme';
import { RegistrationDataImport } from './RegistrationDataImport';

describe('RDI', () => {
  //Open modal
  test('Renders modal after clicking the button', () => {
    const { container, getByTestId } = render(
      <MockedProvider mocks={[]}>
        <ThemeProvider theme={theme}>
          <StyledThemeProvider theme={theme}>
            <MemoryRouter initialEntries={['/afghanistan/registration-data-import']}>
              <RegistrationDataImport />
            </MemoryRouter>
          </StyledThemeProvider>
        </ThemeProvider>
      </MockedProvider>
    )
    const button = container.querySelector('button');
    wait(() => fireEvent.click(button))
    wait(() => expect(container).toContainElement(getByTestId('rdi-dialog')))
  });
  
  //Open modal then click on the download template link
  test('Checks that download template link works', () => {
    const { container, getByTestId, findByRole } = render(
      <MockedProvider mocks={[]}>
        <ThemeProvider theme={theme}>
          <StyledThemeProvider theme={theme}>
            <MemoryRouter initialEntries={['/afghanistan/registration-data-import']}>
              <RegistrationDataImport />
            </MemoryRouter>
          </StyledThemeProvider>
        </ThemeProvider>
      </MockedProvider>
    )
    const button = container.querySelector('button');
    wait(() => fireEvent.click(button))
    wait(() => expect(container).toContainElement(getByTestId('rdi-dialog')))
    const downloadButton = container.querySelector('#download-template');
    wait(() => fireEvent.click(downloadButton))
  })

})
