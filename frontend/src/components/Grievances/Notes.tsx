import { Avatar, Box, Button, Grid, Typography } from '@material-ui/core';
import * as Yup from 'yup';
import { Field, Form, Formik } from 'formik';
import React from 'react';
import styled from 'styled-components';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { UniversalMoment } from '../UniversalMoment';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { OverviewContainerColumn } from '../OverviewContainerColumn';

export function Notes(): React.ReactElement {
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
  const DescMargin = styled.div`
    margin-bottom: 35px;
  `;

  const note = (
    avatar: string,
    name: string,
    date: string,
    description: string,
  ): React.ReactElement => (
    <Grid container>
      <Grid item xs={2}>
        <Avatar src={avatar} alt={`${name} picture`} />
      </Grid>
      <Grid item xs={10}>
        <Grid item xs={12}>
          <Box display='flex' justifyContent='space-between'>
            <Name>{name}</Name>
            <Date>{date}</Date>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <DescMargin>
            <p>{description}</p>
          </DescMargin>
        </Grid>
      </Grid>
    </Grid>
  );
  const d = new window.Date();
  const now = <UniversalMoment withTime>{`${d}`}</UniversalMoment>;

  const mappedNotes = [
    {
      name: 'Martin Scott',
      avatar: 'picture',
      date: '07/15/2020, 4:46 PM',
      description: 'Lorem lorem lorem ipsum',
    },
    {
      name: 'Ben Johnson',
      avatar: 'picture',
      date: '02/10/2020, 4:46 PM',
      description: 'Lorem lorem lorem ipsum',
    },
  ].map((el) => note(el.avatar, el.name, el.date, el.description));

  const initialValues: { [key: string]: string } = {
    newNote: '',
  };

  const validationSchema = Yup.object().shape({
    newNote: Yup.string().required('Note cannot be empty'),
  });

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log(values);
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm, values }) => (
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant='h6'>Notes</Typography>
          </Title>
          <OverviewContainerColumn>
            {mappedNotes}
            <Grid container>
              <Grid item xs={2}>
                <Avatar src='me' alt={`${'me'} picture`} />
              </Grid>
              <Grid item xs={10}>
                <Grid item xs={12}>
                  <Box display='flex' justifyContent='space-between'>
                    <Name>My name</Name>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <DescMargin>
                    <Form>
                      <Field
                        name='newNote'
                        multiline
                        fullWidth
                        variant='filled'
                        label='Add a note ...'
                        component={FormikTextField}
                      />
                      <Box mt={2} display='flex' justifyContent='flex-end'>
                        <Button
                          color='primary'
                          variant='contained'
                          onClick={submitForm}
                        >
                          Add New Note
                        </Button>
                      </Box>
                    </Form>
                  </DescMargin>
                </Grid>
              </Grid>
            </Grid>
          </OverviewContainerColumn>
        </ContainerColumnWithBorder>
      )}
    </Formik>
  );
}
