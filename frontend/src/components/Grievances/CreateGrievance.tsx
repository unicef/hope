import {
  Avatar,
  Box,
  Button,
  DialogActions,
  Grid,
  Typography,
} from '@material-ui/core';
import SearchIcon from '@material-ui/icons/Search';
import * as Yup from 'yup';
import { Field, Form, Formik } from 'formik';
import React from 'react';
import styled from 'styled-components';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { UniversalMoment } from '../UniversalMoment';
import { PageHeader } from '../PageHeader';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { OverviewContainer } from '../OverviewContainer';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';

export function CreateGrievance(): React.ReactElement {
  const Title = styled.div`
    padding-bottom: ${({ theme }) => theme.spacing(8)}px;
  `;
  const NewTicket = styled.div`
    padding: 22px;
  `;
  const DialogFooter = styled.div`
    padding: 12px 16px;
    margin: 0;
    border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
    text-align: right;
  `;
  const BoxWithBorder = styled.div`
    border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
    padding-bottom: 30px;
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
  `;

  const Consent = styled.p`
    font-size: 14px;
    color: #585858;
  `;
  const MarginRightSpan = styled.span`
    margin-right: 5px;
  `;

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
          <Grid container>
            <Grid item xs={9}>
              <NewTicket>
                <ContainerColumnWithBorder>
                  <Grid container>
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
                    <Grid item xs={12}>
                      <BoxWithBorder />
                    </Grid>
                    <Grid item xs={12}>
                      <BoxWithBorder>
                        <Box display='flex' flexDirection='column'>
                          <Consent>
                            Do you give your consent to UNICEF and its partners
                            to view, edit and update your personal details and,
                            if applicable, that of your household and dependants
                            the purpose of the integrity UNICEFs beneficiary
                            management system? Do you declare that the
                            information you have provided is true and correct to
                            the best of your knowledge?
                          </Consent>
                          <Field
                            name='receivedConsent'
                            label='Received Consent*'
                            color='primary'
                            component={FormikCheckboxField}
                          />
                          <Grid item xs={6}>
                            <LookUp>
                              <MarginRightSpan>
                                <SearchIcon />
                              </MarginRightSpan>
                              <span>Look up Household</span>
                            </LookUp>
                          </Grid>
                        </Box>
                      </BoxWithBorder>
                    </Grid>
                  </Grid>

                  <DialogFooter>
                    <DialogActions>
                      <Button onClick={() => console.log('cancel')}>
                        CANCEL
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
