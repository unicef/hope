import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../../theme';
import { Field, Form, Formik } from 'formik';
import styled from 'styled-components';
import { FormikRadioGroup } from './FormikRadioGroup';

export default {
  component: FormikRadioGroup,
  title: 'FormikRadioGroup',
};

const FieldWrapper = styled.div`
  width: 300px;
`;

const sampleChoices = [{name: 'Sample', value: 'sample'}, {name: 'Choice', value: 'choice'}]

export const RadioGroup = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <Formik
          initialValues={{ choiceField: sampleChoices[0].value }}
          onSubmit={(values) => {
            return console.log(values);
          }}
        >
          {() => (
            <Form>
              <FieldWrapper>
                <Field
                  name='choiceField'
                  label='Sample label'
                  choices={sampleChoices}
                  component={FormikRadioGroup}
                />
              </FieldWrapper>
            </Form>
          )}
        </Formik>
      </StyledThemeProvider>
    </ThemeProvider>
  );
};