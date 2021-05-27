import {Box, Button, Paper, Typography} from '@material-ui/core';
import styled from 'styled-components';
import React, {ReactElement, useState} from 'react';
import {Formik} from 'formik';
import {GrievanceTicketQuery, useApproveHouseholdDataChangeMutation,} from '../../__generated__/graphql';
import {ConfirmationDialog} from '../ConfirmationDialog';
import {GRIEVANCE_TICKET_STATES} from '../../utils/constants';
import {useSnackbar} from '../../hooks/useSnackBar';
import {RequestedHouseholdDataChangeTable} from './RequestedHouseholdDataChangeTable';

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
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): React.ReactElement {
  const { showMessage } = useSnackbar();
  const getConfirmationText = (values): string => {
    const allSelected =
      values.selected.length + values.selectedFlexFields.length || 0;
    return `You approved ${allSelected} change${
      allSelected === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };
  const [mutate] = useApproveHouseholdDataChangeMutation();
  const householdData = {
    ...ticket.householdDataUpdateTicketDetails.householdData,
  };
  let allApprovedCount = 0;
  const flexFields = householdData?.flex_fields || {};
  delete householdData.flex_fields;
  const flexFieldsEntries = Object.entries(flexFields);
  const entries = Object.entries(householdData);
  allApprovedCount += entries.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;
  allApprovedCount += flexFieldsEntries.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);
  const shouldShowEditButton = (values): boolean =>
    (values.selected.length || values.selectedFlexFields.length) &&
    !isEdit &&
    ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;

  const areAllApproved = (values): boolean => {
    const selectedCount =
      values.selected.length + values.selectedFlexFields.length;
    const countAll = entries.length + flexFieldsEntries.length;
    return selectedCount === countAll;
  };

  const getApprovalButton = (values, submitForm): ReactElement => {
    if (areAllApproved(values)) {
      return (
        <Button
          onClick={submitForm}
          variant='contained'
          color='primary'
          disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
        >
          Approve
        </Button>
      );
    }
    return (
      <ConfirmationDialog title='Warning' content={getConfirmationText(values)}>
        {(confirm) => (
          <Button
            onClick={confirm(() => submitForm())}
            variant='contained'
            color='primary'
            disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
          >
            Approve
          </Button>
        )}
      </ConfirmationDialog>
    );
  };
  return (
    <Formik
      initialValues={{
        selected: entries
          .filter((row: [string, { approve_status: boolean }]) => {
            return row[1].approve_status;
          })
          .map((row) => row[0]),
        selectedFlexFields: flexFieldsEntries
          .filter((row: [string, { approve_status: boolean }]) => {
            return row[1].approve_status;
          })
          .map((row) => row[0]),
      }}
      onSubmit={async (values) => {
        const householdApproveData = values.selected.reduce((prev, curr) => {
          // eslint-disable-next-line no-param-reassign
          prev[curr] = true;
          return prev;
        }, {});
        const flexFieldsApproveData = values.selectedFlexFields.reduce(
          (prev, curr) => {
            // eslint-disable-next-line no-param-reassign
            prev[curr] = true;
            return prev;
          },
          {},
        );
        try {
          await mutate({
            variables: {
              grievanceTicketId: ticket.id,
              householdApproveData: JSON.stringify(householdApproveData),
              flexFieldsApproveData: JSON.stringify(flexFieldsApproveData),
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
              {shouldShowEditButton(values) ? (
                <Button
                  onClick={() => setEdit(true)}
                  variant='outlined'
                  color='primary'
                  disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
                >
                  EDIT
                </Button>
              ) : (
                canApproveDataChange && getApprovalButton(values, submitForm)
              )}
            </Box>
          </Title>
          <RequestedHouseholdDataChangeTable
            ticket={ticket}
            setFieldValue={setFieldValue}
            isEdit={isEdit}
            values={values}
          />
        </StyledBox>
      )}
    </Formik>
  );
}
