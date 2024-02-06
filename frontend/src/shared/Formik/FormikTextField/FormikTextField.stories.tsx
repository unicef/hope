import React from 'react';
import { ThemeProvider } from '@mui/material';
import styled, { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { Field, Form, Formik } from 'formik';
import { theme } from '../../../theme';
import { FormikTextField } from './FormikTextField';

export default {
  component: FormikTextField,
  title: 'FormikTextField',
};

const FieldWrapper = styled.div`
  width: 300px;
`;

export function TextField() {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <Formik
          initialValues={{ requiredTextField: '', textField: '' }}
          onSubmit={(values) => console.log(values)}
        >
          {() => (
            <Form>
              <FieldWrapper>
                <Field
                  name="textField"
                  label="Text field"
                  type="text"
                  fullWidth
                  component={FormikTextField}
                />
              </FieldWrapper>
              <FieldWrapper>
                <Field
                  name="requiredTextField"
                  label="Required text field"
                  type="text"
                  fullWidth
                  required
                  component={FormikTextField}
                />
              </FieldWrapper>
            </Form>
          )}
        </Formik>
      </StyledThemeProvider>
    </ThemeProvider>
  );
}
