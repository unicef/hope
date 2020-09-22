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

export function CreateGrievance(): React.ReactElement {
  const Container = styled.div`
    display: flex;
    flex: 1;
    width: 100%;
    background-color: #fff;
    padding: ${({ theme }) => theme.spacing(8)}px
      ${({ theme }) => theme.spacing(11)}px;
    flex-direction: column;
    border-color: #b1b1b5;
    border-bottom-width: 1px;
    border-bottom-style: solid;
  `;
  const OverviewContainer = styled.div`
    display: flex;
    align-items: center;
    flex-direction: column;
  `;

  const Title = styled.div`
    padding-bottom: ${({ theme }) => theme.spacing(8)}px;
  `;
  const Name = styled.span`
    font-size: 16px;
  `;
  const Date = styled.span`
    font-size: 12px;
    color: #848484;
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
          <Container>
            <Title>
              <Typography variant='h6'>Create Grievance</Typography>
            </Title>
            <OverviewContainer>modal content</OverviewContainer>
          </Container>
        </>
      )}
    </Formik>
  );
}
