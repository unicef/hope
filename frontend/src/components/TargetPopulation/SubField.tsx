import React from 'react';
import styled from 'styled-components';
import { Field } from 'formik';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikDecimalField } from '../../shared/Formik/FormikDecimalField';
import { FormikAutocomplete } from '../../shared/Formik/FormikAutocomplete';

const FlexWrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;
const InlineField = styled.div`
  width: 48%;
`;

export const SubField = ({ field, index, baseName }): React.ReactElement => {
  switch (field.fieldAttribute.type) {
    case 'DECIMAL':
      return (
        <FlexWrapper>
          <InlineField>
            <Field
              name={`${baseName}.value.from`}
              label={`${field.fieldAttribute.labelEn} from`}
              variant='outlined'
              fullWidth
              component={FormikDecimalField}
            />
          </InlineField>
          <InlineField>
            <Field
              name={`${baseName}.value.to`}
              label={`${field.fieldAttribute.labelEn} to`}
              variant='outlined'
              fullWidth
              component={FormikDecimalField}
            />
          </InlineField>
        </FlexWrapper>
      );
    case 'DATE':
      return (
        <FlexWrapper>
          <InlineField>
            <Field
              name={`${baseName}.value.from`}
              label={`${field.fieldAttribute.labelEn} from`}
              fullWidth
              component={FormikDateField}
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </InlineField>
          <InlineField>
            <Field
              name={`${baseName}.value.to`}
              label={`${field.fieldAttribute.labelEn} to`}
              fullWidth
              component={FormikDateField}
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </InlineField>
        </FlexWrapper>
      );
    case 'INTEGER':
      return (
        <FlexWrapper>
          <InlineField>
            <Field
              name={`${baseName}.value.from`}
              label={`${field.fieldAttribute.labelEn} from`}
              type='number'
              integer
              variant='outlined'
              fullWidth
              component={FormikTextField}
            />
          </InlineField>
          <InlineField>
            <Field
              name={`${baseName}.value.to`}
              label={`${field.fieldAttribute.labelEn} to`}
              type='number'
              integer
              variant='outlined'
              fullWidth
              component={FormikTextField}
            />
          </InlineField>
        </FlexWrapper>
      );
    case 'SELECT_ONE':
      return field.fieldName.includes('admin') ? (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          choices={field.fieldAttribute.choices}
          index={index}
          component={FormikAutocomplete}
        />
      ) : (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          choices={field.fieldAttribute.choices}
          index={index}
          component={FormikSelectField}
        />
      );
    case 'SELECT_MANY':
      return (
        <Field
          name={`${baseName}.value`}
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
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          fullWidth
          variant='outlined'
          component={FormikTextField}
        />
      );
    case 'BOOL':
      return (
        <Field
          name={`${baseName}.value`}
          label={`${field.fieldAttribute.labelEn}`}
          choices={[
            {
              admin: null,
              labelEn: 'Yes',
              labels: [{ label: 'Yes', language: 'English(EN)' }],
              listName: null,
              value: 'True',
            },
            {
              admin: null,
              labelEn: 'No',
              labels: [{ label: 'No', language: 'English(EN)' }],
              listName: null,
              value: 'False',
            },
          ]}
          index={index}
          component={FormikSelectField}
        />
      );
    default:
      return <p>{field.fieldAttribute.type}</p>;
  }
};
