import { Avatar, Box, Button, Grid, Typography } from '@material-ui/core';
import * as Yup from 'yup';
import { Field, Form, Formik } from 'formik';
import React from 'react';
import styled from 'styled-components';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { UniversalMoment } from '../UniversalMoment';
import { PageHeader } from '../PageHeader';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContainerWithBorder } from '../ContainerWithBorder';
import { OverviewContainer } from '../OverviewContainer';

export function CreateGrievance(): React.ReactElement {
  const Title = styled.div`
    padding-bottom: ${({ theme }) => theme.spacing(8)}px;
  `;
  const NewTicket = styled.div`
    padding: 22px;
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
                <ContainerWithBorder>
                  <Title>
                    <Typography variant='h6'>Create Grievance</Typography>
                  </Title>
                  <OverviewContainer>modal content</OverviewContainer>
                </ContainerWithBorder>
              </NewTicket>
            </Grid>
          </Grid>
        </>
      )}
    </Formik>
  );
}
