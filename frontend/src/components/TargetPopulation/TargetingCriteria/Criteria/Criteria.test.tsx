import React from 'react';
import { render, wait, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { Criteria } from './Criteria';
import { theme } from '../../../../theme';

const EqualsCriteria:any = [{
  arguments: ["OTHER"],
  comparisionMethod: "EQUALS",
  isFlexField: false,
  fieldName: 'residence_status',
  fieldAttribute: {
    labelEn: 'Residence Status',
    name: 'residence_status',
    type: 'SELECT_ONE',
    choices: [{
      value: 'OTHER',
      labelEn: "Other",
    }]
  }
}]


describe('Criteria card', () => {
  test('Renders criteria without errors', () => {
    const { container } = render(
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <Criteria rules={EqualsCriteria} isEdit={false} canRemove={false} />
        </StyledThemeProvider>
      </ThemeProvider>
    )
  })
  test('Triggers remove function for criteria in edit state', () => {
    const removeFunction = jest.fn();
    const { container } = render(
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <Criteria rules={EqualsCriteria} removeFunction={removeFunction} isEdit={false} canRemove={false} />
        </StyledThemeProvider>
      </ThemeProvider>
    )
    const removeButton = document.querySelector("[data-testid='remove-button']")
    wait(() => fireEvent.click(removeButton))
    wait(() => expect(removeFunction).toBeCalled())
  })
  test('Triggers edit function for criteria in edit state', () => {
    const editFunction = jest.fn();
    const { container } = render(
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <Criteria rules={EqualsCriteria} editFunction={editFunction} isEdit={false} canRemove={false} />
        </StyledThemeProvider>
      </ThemeProvider>
    )
    const removeButton = document.querySelector("[data-testid='edit-button']")
    wait(() => fireEvent.click(removeButton))
    wait(() => expect(editFunction).toBeCalled())
  })
})
