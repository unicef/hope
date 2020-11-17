import React from 'react';
import { Grid, Typography } from '@material-ui/core';
import styled from 'styled-components';
import { Field } from 'formik';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';

const Title = styled.div`
  width: 100%;
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;
export const AddIndividualDataChange = (): React.ReactElement => {
  return (
    <>
      <Title>
        <Typography variant='h6'>Individual Data</Typography>
      </Title>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Grid item xs={6}>
            <Field
              name='givenName'
              fullWidth
              variant='outlined'
              label='First Name'
              component={FormikTextField}
            />
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Grid item xs={6}>
            <Field
              name='middleName'
              fullWidth
              variant='outlined'
              label='Middle Name'
              component={FormikTextField}
            />
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Grid item xs={6}>
            <Field
              name='familyName'
              fullWidth
              variant='outlined'
              label='Last Name'
              component={FormikTextField}
            />
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Grid item xs={6}>
            <Field
              name='sex'
              label='Gender'
              color='primary'
              choices={[
                { value: 'FEMALE', name: 'Female' },
                { value: 'MALE', name: 'Male' },
              ]}
              component={FormikSelectField}
            />
          </Grid>
        </Grid>
        <Grid item xs={12}>
          <Grid item xs={6}>
            <Field
              name='birthDate'
              label='Date of Birth'
              component={FormikDateField}
              fullWidth
              decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            />
          </Grid>
        </Grid>
        <Grid item xs={6}>
          <Field
            name='idType'
            label='ID Type'
            color='primary'
            choices={[
              { value: 'PASSPORT', name: 'Passport' },
              { value: 'ID DOCUMENT', name: 'ID Document' },
            ]}
            component={FormikSelectField}
          />
        </Grid>
        <Grid item xs={6}>
          <Field
            name='idNumber'
            label='ID Number'
            fullWidth
            variant='outlined'
            component={FormikTextField}
          />
        </Grid>
      </Grid>
    </>
  );
};
