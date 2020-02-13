import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../../theme';
import { Field, Form, Formik } from 'formik';
import styled from 'styled-components';
import { FormikSwitchField } from './FormikSwitchField';

export default {
  component: FormikSwitchField,
  title: 'FormikSwitchField',
};

const FieldWrapper = styled.div`
  width: 300px;
`;

export const SwitchField = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <Formik
          initialValues={{ switchField: false }}
          onSubmit={(values) => {
            return console.log(values);
          }}
        >
          {() => (
            <Form>
              <FieldWrapper>
                <Field
                  name='switchField'
                  label='Switch field'
                  color='primary'
                  component={FormikSwitchField}
                />
              </FieldWrapper>
            </Form>
          )}
        </Formik>
      </StyledThemeProvider>
    </ThemeProvider>
  );
};
