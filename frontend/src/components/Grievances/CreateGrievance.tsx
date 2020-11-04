import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import * as Yup from 'yup';
import { Field, Formik } from 'formik';
import { Box, Button, DialogActions, Grid } from '@material-ui/core';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { PageHeader } from '../PageHeader';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { Consent } from './Consent';
import { LookUpSection } from './LookUpSection';

const BoxPadding = styled.div`
  padding: 15px 0;
`;
const NewTicket = styled.div`
  padding: 20px;
`;
const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const BoxWithBorderBottom = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;
const BoxWithBorders = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  padding: 15px 0;
`;

export function CreateGrievance(): React.ReactElement {
  const businessArea = useBusinessArea();

  const initialValues: { [key: string]: string } = {
    selectedHousehold: '',
    selectedIndividual: '',
  };

  const validationSchema = Yup.object().shape({
    selectedHousehold: Yup.string().required('Household has to be selected'),
    selectedIndividual: Yup.string().required('Individual has to be selected'),
  });

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Grievance and Feedback',
      to: `/${businessArea}/grievance-and-feedback/`,
    },
  ];

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log(values);
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm, values, setFieldValue }) => (
        <>
          <PageHeader title='New Ticket' breadCrumbs={breadCrumbsItems} />
          <Grid container spacing={3}>
            <Grid item xs={8}>
              <NewTicket>
                <ContainerColumnWithBorder>
                  <Grid container spacing={3}>
                    <Grid item xs={6}>
                      <Field
                        name='category'
                        label='Category*'
                        variant='outlined'
                        choices={[
                          {
                            value: 'Positive Feedback',
                            name: 'Positive Feedback',
                          },
                          {
                            value: 'Negative Feedback',
                            name: 'Negative Feedback',
                          },
                          {
                            value: 'Grievance Complaint',
                            name: 'Grievance Complaint',
                          },
                          {
                            value: 'Payment Verification Issue',
                            name: 'Payment Verification Issue',
                          },
                          { value: 'Referral', name: 'Referral' },
                          { value: 'Data Change', name: 'Data Change' },
                          {
                            value: 'Sensitive Grievance',
                            name: 'Sensitive Grievance',
                          },
                        ]}
                        component={FormikSelectField}
                      />
                    </Grid>
                  </Grid>
                  <BoxWithBorders>
                    <Box display='flex' flexDirection='column'>
                      <Consent />
                      <Field
                        name='receivedConsent'
                        label='Received Consent*'
                        color='primary'
                        component={FormikCheckboxField}
                      />
                      <LookUpSection
                        category={values.category}
                        values={values}
                        onValueChange={setFieldValue}
                      />
                    </Box>
                  </BoxWithBorders>
                  <BoxWithBorderBottom>
                    <Grid container spacing={3}>
                      <Grid item xs={6}>
                        <Field
                          name='assignedTo'
                          label='Assigned to'
                          variant='outlined'
                          choices={[
                            {
                              value: 'User1',
                              name: 'User1',
                            },
                            {
                              value: 'User2',
                              name: 'User2',
                            },
                            {
                              value: 'User3',
                              name: 'User3',
                            },
                          ]}
                          component={FormikSelectField}
                        />
                      </Grid>
                    </Grid>
                  </BoxWithBorderBottom>
                  <BoxPadding>
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <Field
                          name='Description'
                          multiline
                          fullWidth
                          variant='outlined'
                          label='Description'
                          component={FormikTextField}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='administrativeLevel2'
                          label='Administrative Level 2'
                          variant='outlined'
                          choices={[
                            {
                              value: 'Admin1',
                              name: 'Admin1',
                            },
                            {
                              value: 'Admin2',
                              name: 'Admin2',
                            },
                            {
                              value: 'Admin3',
                              name: 'Admin3',
                            },
                          ]}
                          component={FormikSelectField}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='area'
                          fullWidth
                          variant='outlined'
                          label='Area / Village / Pay point'
                          component={FormikTextField}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='languagesSpoken'
                          label='Languages Spoken'
                          variant='outlined'
                          choices={[
                            {
                              value: 'English',
                              name: 'English',
                            },
                            {
                              value: 'French',
                              name: 'French',
                            },
                            {
                              value: 'Spanish',
                              name: 'Spanish',
                            },
                          ]}
                          component={FormikSelectField}
                        />
                      </Grid>
                    </Grid>
                  </BoxPadding>

                  <DialogFooter>
                    <DialogActions>
                      <Button
                        component={Link}
                        to={`/${businessArea}/grievance-and-feedback`}
                      >
                        Cancel
                      </Button>
                      <Button
                        color='primary'
                        variant='contained'
                        onClick={submitForm}
                      >
                        Save
                      </Button>
                    </DialogActions>
                  </DialogFooter>
                </ContainerColumnWithBorder>
              </NewTicket>
            </Grid>
          </Grid>
        </>
      )}
    </Formik>
  );
}
