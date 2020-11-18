import React from 'react';
import { Button, Grid, Typography } from '@material-ui/core';
import styled from 'styled-components';
import { Field } from 'formik';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import camelCase from 'lodash/camelCase';
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
  fields: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'];
}
export const EditIndividualDataChangeField = ({
  fields,
}: AddIndividualDataChangeFieldProps): React.ReactElement => {
  return null;
};

export const EditIndividualDataChange = (): React.ReactElement => {
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
        <EditIndividualDataChangeField
          fields={data.allAddIndividualsFieldsAttributes}
        />
        <Grid item xs={4}>
          <Button>Add</Button>
        </Grid>
      </Grid>
    </>
  );
};
