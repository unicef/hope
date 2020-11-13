import React from 'react';
import { Avatar, Box, Button, Grid, Typography } from '@material-ui/core';
import { useParams } from 'react-router-dom';
import * as Yup from 'yup';
import { Field, Form, Formik } from 'formik';
import styled from 'styled-components';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { UniversalMoment } from '../UniversalMoment';
import { ContainerColumnWithBorder } from '../ContainerColumnWithBorder';
import { OverviewContainerColumn } from '../OverviewContainerColumn';
import {
  GrievanceTicketQuery,
  useCreateGrievanceTicketNoteMutation,
  useMeQuery,
} from '../../__generated__/graphql';
import { renderUserName } from '../../utils/utils';
import { GrievanceTicket } from '../../apollo/queries/GrievanceTicket';

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

export function Notes({
  notes,
}: {
  notes: GrievanceTicketQuery['grievanceTicket']['ticketNotes'];
}): React.ReactElement {
  const { data: meData, loading: meLoading } = useMeQuery({
    fetchPolicy: 'cache-and-network',
  });

  const { id } = useParams();
  const [mutate] = useCreateGrievanceTicketNoteMutation();

  if (meLoading) {
    return null;
  }

  const note = (
    name: string,
    date: string,
    description: string,
  ): React.ReactElement => (
    <Grid container>
      <Grid item xs={2}>
        <Avatar alt={`${name} picture`} src='/static/images/avatar/1.jpg' />
      </Grid>
      <Grid item xs={10}>
        <Grid item xs={12}>
          <Box display='flex' justifyContent='space-between'>
            <Name>{name}</Name>
            <Date>
              <UniversalMoment withTime>{date}</UniversalMoment>
            </Date>
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

  const mappedNotes = notes?.edges?.map((el) =>
    note(
      renderUserName(el.node.createdBy),
      el.node.createdAt,
      el.node.description,
    ),
  );

  const initialValues: { [key: string]: string } = {
    newNote: '',
  };

  const validationSchema = Yup.object().shape({
    newNote: Yup.string().required('Note cannot be empty'),
  });

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values, { resetForm }) => {
        mutate({
          variables: {
            noteInput: { ticket: id, description: values.newNote },
          },
          refetchQueries: () => [{ query: GrievanceTicket, variables: { id } }],
        });
        resetForm({});
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <ContainerColumnWithBorder>
          <Title>
            <Typography variant='h6'>Notes</Typography>
          </Title>
          <OverviewContainerColumn>
            {mappedNotes}
            <Grid container>
              <Grid item xs={2}>
                <Avatar
                  src={`${meData.me.firstName || meData.me.email}`}
                  alt={`${meData.me.firstName || meData.me.email} picture`}
                />
              </Grid>
              <Grid item xs={10}>
                <Grid item xs={12}>
                  <Box display='flex' justifyContent='space-between'>
                    <Name>{renderUserName(meData.me)}</Name>
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
