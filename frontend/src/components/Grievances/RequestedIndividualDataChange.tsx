import { Box, Button, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React from 'react';
import { GrievanceTicketQuery } from '../../__generated__/graphql';
import { Formik } from 'formik';
import { RequestedIndividualDataChangeTable } from './RequestedIndividualDataChangeTable';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { selectFields } from '../../utils/utils';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function RequestedIndividualDataChange({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const getConfirmationText = (values) => {
    return `You approved ${values.selected.length || 0} change${
      values.selected.length === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };
  return (
    <Formik
      initialValues={{ selected: [] }}
      onSubmit={(values) => {
        console.log(values);
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
        <StyledBox>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>Requested Data Change</Typography>
              <ConfirmationDialog
                title='Warning'
                content={getConfirmationText(values)}
              >
                {(confirm) => (
                  <Button
                    onClick={confirm(() => submitForm())}
                    variant='contained'
                    color='primary'
                    disabled={
                      !values.selected.length ||
                      ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                    }
                  >
                    Approve
                  </Button>
                )}
              </ConfirmationDialog>
            </Box>
          </Title>
          <RequestedIndividualDataChangeTable
            ticket={ticket}
            setFieldValue={setFieldValue}
          />
        </StyledBox>
      )}
    </Formik>
  );
}
