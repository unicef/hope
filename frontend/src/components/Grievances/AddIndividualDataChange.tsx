import React from 'react';
import { Grid, Typography } from '@material-ui/core';
import styled from 'styled-components';
import { Field } from 'formik';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import {
  AllAddIndividualFieldsQuery,
  useAllAddIndividualFieldsQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export interface AddIndividualDataChangeFieldProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
}
export const AddIndividualDataChangeField = ({
  field,
}: AddIndividualDataChangeFieldProps): React.ReactElement => {
  let fieldProps;
  switch (field.type) {
    case 'STRING':
      fieldProps = {
        component: FormikTextField,
      };
      break;
    case 'SELECT_ONE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'SELECT_MANY':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
        multiple: true,
      };
      break;
    case 'SELECT_MULTIPLE':
      fieldProps = {
        choices: field.choices,
        component: FormikSelectField,
      };
      break;
    case 'DATE':
      fieldProps = {
        component: FormikDateField,
        decoratorEnd: <CalendarTodayRoundedIcon color='disabled' />,
      };
      break;

    case 'BOOL':
      fieldProps = {
        component: FormikCheckboxField,
      };
      break;
    default:
      fieldProps = {};
  }
  return (
    <>
      <Grid item xs={6}>
        <Field
          name={field.name}
          fullWidth
          variant='outlined'
          label={field.labelEn}
          required={field.required}
          {...fieldProps}
        />
      </Grid>
      <Grid item xs={6}/>
    </>
  );
};

export const AddIndividualDataChange = (): React.ReactElement => {
  const { data, loading } = useAllAddIndividualFieldsQuery();
  if (loading) {
    return <LoadingComponent />;
  }
  return (
    <>
      <Title>
        <Typography variant='h6'>Individual Data</Typography>
      </Title>
      <Grid container spacing={3}>
        {data.allAddIndividualsFieldsAttributes.map((item) => (
          <AddIndividualDataChangeField field={item} />
        ))}
      </Grid>
    </>
  );
};
