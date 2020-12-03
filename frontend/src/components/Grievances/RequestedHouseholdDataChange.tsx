import { Box, Button, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React, { useState } from 'react';
import { Formik } from 'formik';
import mapKeys from 'lodash/mapKeys';
import camelCase from 'lodash/camelCase';
import {
  GrievanceTicketQuery,
  useApproveHouseholdDataChangeMutation,
} from '../../__generated__/graphql';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { useSnackbar } from '../../hooks/useSnackBar';
import { RequestedHouseholdDataChangeTable } from './RequestedHouseholdDataChangeTable';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function RequestedHouseholdDataChange({
  ticket,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const { showMessage } = useSnackbar();
  const getConfirmationText = (values) => {
    return `You approved ${values.selected.length || 0} change${
      values.selected.length === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };
  const [mutate] = useApproveHouseholdDataChangeMutation();
  const householdData = {
    ...ticket.householdDataUpdateTicketDetails.householdData,
  };
  let allApprovedCount = 0;
  const entries = Object.entries(householdData);
  allApprovedCount += entries.filter(
    ([key, value]: [string, { approve_status: boolean }]) =>
      value.approve_status,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);

  return (
    <Formik
      initialValues={{
        selected: entries
          .filter((row) => {
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => camelCase(row[0])),
      }}
      onSubmit={async (values) => {
        const householdApproveData = values.selected.reduce((prev, curr) => {
          // eslint-disable-next-line no-param-reassign
          prev[curr] = true;
          return prev;
        }, {});
        try {
          await mutate({
            variables: {
              grievanceTicketId: ticket.id,
              householdApproveData: JSON.stringify(householdApproveData),
            },
          });
          showMessage('Changes Approved');
          setEdit(values.selected.length === 0);
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
        <StyledBox>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>Requested Data Change</Typography>
              {values.selected.length && !isEdit ? (
                <Button
                  onClick={() => setEdit(true)}
                  variant='outlined'
                  color='primary'
                >
                  EDIT
                </Button>
              ) : (
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
                        ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                      }
                    >
                      Approve
                    </Button>
                  )}
                </ConfirmationDialog>
              )}
            </Box>
          </Title>
          <RequestedHouseholdDataChangeTable
            ticket={ticket}
            setFieldValue={setFieldValue}
            isEdit={isEdit}
          />
        </StyledBox>
      )}
    </Formik>
  );
}
