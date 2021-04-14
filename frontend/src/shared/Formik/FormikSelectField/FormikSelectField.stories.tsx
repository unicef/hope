import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../../theme';
import { Field, Form, Formik } from 'formik';
import styled from 'styled-components';
import { FormikSelectField } from './FormikSelectField';

export default {
  component: FormikSelectField,
  title: 'FormikSelectField',
};

const FieldWrapper = styled.div`
  width: 300px;
`;

const choices = [{name: 'Sample choice', value: 'SAMPLE'}, {name: 'Sample choice 2', value: 'ANOTHER_SAMPLE'}]

export const SelectField = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <Formik
          initialValues={{ requiredTextField: '', textField: '' }}
          onSubmit={(values) => {
            return console.log(values);
          }}
        >
          {() => (
            <Form>
              <FieldWrapper>
                <Field
                  name='selectField'
                  label='Select field'
                  fullWidth
                  required
                  choices={choices}
                  component={FormikSelectField}
                />
              </FieldWrapper>
            </Form>
          )}
        </Formik>
      </StyledThemeProvider>
    </ThemeProvider>
  );
};
