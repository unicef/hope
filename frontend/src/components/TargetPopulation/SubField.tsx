import React from 'react';
import styled from 'styled-components';
import { Field } from 'formik';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;
const InlineField = styled.div`
  width: 48%;
`;

export const SubField = (field, index) => {
    switch (field.fieldAttribute.type) {
      case 'INTEGER':
        return (
          <FlexWrapper>
            <InlineField>
              <Field
                name={`filters[${index}].value.from`}
                label={`${field.fieldAttribute.labelEn} from`}
                type='number'
                variant='outlined'
                fullWidth
                component={FormikTextField}
              />
            </InlineField>
            <InlineField>
              <Field
                name={`filters[${index}].value.to`}
                label={`${field.fieldAttribute.labelEn} to`}
                type='number'
                variant='outlined'
                fullWidth
                component={FormikTextField}
              />
            </InlineField>
          </FlexWrapper>
        );
      case 'SELECT_ONE':
        return (
          <Field
            name={`filters[${index}].value`}
            label={`${field.fieldAttribute.labelEn}`}
            choices={field.fieldAttribute.choices}
            index={index}
            component={FormikSelectField}
          />
        );
      case 'SELECT_MANY':
        return (
          <Field
            name={`filters[${index}].value`}
            label={`${field.fieldAttribute.labelEn}`}
            choices={field.fieldAttribute.choices}
            index={index}
            multiple
            component={FormikSelectField}
          />
        );
      case 'STRING':
        return (
          <Field
            name={`filters[${index}].value`}
            label={`${field.fieldAttribute.labelEn}`}
            fullWidth
            component={FormikTextField}
          />
        );
      default:
        return <p>{field.fieldAttribute.type}</p>;
    }
  };