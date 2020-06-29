import React from 'react';
import { render, fireEvent, wait, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MockedProvider } from '@apollo/react-testing';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../../theme';
import { RegistrationDataImport } from './RegistrationDataImport';

const MockedWrapper = ({ children }) => (
  <MockedProvider mocks={[]}>
  <ThemeProvider theme={theme}>
    <StyledThemeProvider theme={theme}>
      <MemoryRouter initialEntries={['/afghanistan/registration-data-import']}>
        {children}
      </MemoryRouter>
    </StyledThemeProvider>
  </ThemeProvider>
</MockedProvider>
)

describe('RDI', () => {
  //Open modal
  test('Renders modal after clicking the button', () => {
    const { container, getByTestId } = render(
      <MockedWrapper children={<RegistrationDataImport />} />
    )
    const button = container.querySelector('button');
    wait(() => fireEvent.click(button))
    wait(() => expect(container).toContainElement(getByTestId('rdi-dialog')))
  });
  
  //Open modal then click on the download template link
  test('Checks that download template link works', () => {
    const { container, getByTestId } = render(
      <MockedWrapper children={<RegistrationDataImport />} />
    )
    const button = container.querySelector('button');
    wait(() => fireEvent.click(button))
    wait(() => expect(container).toContainElement(getByTestId('rdi-dialog')))
    const downloadButton = container.querySelector('#download-template');
    wait(() => fireEvent.click(downloadButton))
  })

  test('Import from Excel toggle Upload File dropzone', () => {
    const { container, getByTestId } = render(
      <MockedWrapper children={<RegistrationDataImport />} />
    )
    const button = container.querySelector('button');
    wait(() => fireEvent.click(button))
    wait(() => expect(container).toContainElement(getByTestId('rdi-dialog')))
    const comboBox = container.querySelector('#type-combo-box')
    wait(() => fireEvent.change(comboBox, {
      target: {value: 'excel'}
    }));
    wait(() => expect(container).toContainElement(getByTestId('dropzone')))
  })

  test('Import from kobo shows import from field', () => {
    const { container, getByTestId } = render(
      <MockedWrapper children={<RegistrationDataImport />} />
    )
    const button = container.querySelector('button');
    wait(() => fireEvent.click(button))
    wait(() => expect(container).toContainElement(getByTestId('rdi-dialog')))
    const comboBox = container.querySelector('#type-combo-box')
    wait(() => fireEvent.change(comboBox, {
      target: {value: 'excel'}
    }));
    wait(() => expect(container).toContainElement(getByTestId('import-from-select')))
  })
})
