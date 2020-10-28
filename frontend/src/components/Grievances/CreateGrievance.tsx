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
import { LookUpHouseholdIndividual } from './LookUpHouseholdIndividual';

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
const LookUp = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  border: 1.5px solid #043e91;
  border-radius: 5px;
  color: #033f91;
  font-size: 16px;
  text-align: center;
  padding: 25px;
  font-weight: 500;
  cursor: pointer;
`;

const Consent = styled.p`
  font-size: 14px;
  color: #585858;
`;
const MarginRightSpan = styled.span`
  margin-right: 5px;
`;
const StyledLink = styled(Link)`
  text-decoration: none;
`;

export function CreateGrievance(): React.ReactElement {
  const businessArea = useBusinessArea();

  const initialValues: { [key: string]: string } = {
    newNote: '',
  };

  const validationSchema = Yup.object().shape({
    newNote: Yup.string().required('Note cannot be empty'),
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
      {({ submitForm, values }) => (
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
                        variant='filled'
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
                      <Consent>
                        Do you give your consent to UNICEF and its partners to
                        view, edit and update your personal details and, if
                        applicable, that of your household and dependants the
                        purpose of the integrity UNICEFs beneficiary management
                        system? Do you declare that the information you have
                        provided is true and correct to the best of your
                        knowledge?
                      </Consent>
                      <Field
                        name='receivedConsent'
                        label='Received Consent*'
                        color='primary'
                        component={FormikCheckboxField}
                      />
                      <Grid container spacing={3}>
                        <Grid item xs={6}>
                          <LookUpHouseholdIndividual />
                        </Grid>
                      </Grid>
                    </Box>
                  </BoxWithBorders>
                  <BoxWithBorderBottom>
                    <Grid container spacing={3}>
                      <Grid item xs={6}>
                        <Field
                          name='assignedTo'
                          label='Assigned to'
                          variant='filled'
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
                          variant='filled'
                          label='Description'
                          component={FormikTextField}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='administrativeLevel2'
                          label='Administrative Level 2'
                          variant='filled'
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
                          variant='filled'
                          label='Area / Village / Pay point'
                          component={FormikTextField}
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <Field
                          name='languagesSpoken'
                          label='Languages Spoken'
                          variant='filled'
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
                        onClick={() => console.log('save')}
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
