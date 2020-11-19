import { Box, Button, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React from 'react';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { EditIndividualGrievanceDetailsTable } from './EditIndividualGrievanceDetailsTable';
import { Formik } from 'formik';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function EditIndividualGrievanceDetails({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  return (
    <Formik
      initialValues={{ selected: [] }}
      onSubmit={(values) => {
        console.log(values);
      }}
    >
      {({ submitForm, setFieldValue }) => (
        <StyledBox>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>Requested Data Change</Typography>
              <Button onClick={submitForm} variant='contained' color='primary'>
                Approve
              </Button>
            </Box>
          </Title>
          <EditIndividualGrievanceDetailsTable
            ticket={ticket}
            setFieldValue={setFieldValue}
          />
        </StyledBox>
      )}
    </Formik>
  );
}
