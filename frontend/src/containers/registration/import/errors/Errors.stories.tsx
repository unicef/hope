import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import styled from 'styled-components';
import { theme } from '../../../../theme';
import { ErrorsKobo } from './KoboErrors';
import { Errors } from './PlainErrors';

export default {
  component: ErrorsKobo,
  title: 'RDI Errors',
};

const ErrorWrapper = styled.div`
  width: 320px;
`

const errorsListKobo = [{
    header: 'Error header',
    message: 'Error message'
  }, {
    header: 'Error header 2',
    message: 'Error message 2'
  }
];

const errorsListPlain = [
  {
    rowNumber: 1,
    message: 'Error in row 1'
  },
  {
    rowNumber: 2,
    message: 'Cell cannot be empty'
  }
]

export const KoboError = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <ErrorWrapper>
          <h4>Sample Kobo Error</h4>
          <ErrorsKobo errors={errorsListKobo} />
        </ErrorWrapper>
        <ErrorWrapper>
          <h4>Sample Plain Errors (possible in importing xlsx)</h4>
          <Errors errors={errorsListPlain} />
        </ErrorWrapper>
      </StyledThemeProvider>
    </ThemeProvider>
  );
};
