import { Box, Button, Typography } from '@material-ui/core';
import { Formik } from 'formik';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '../../hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import {
  GrievanceTicketNode,
  useApproveHouseholdDataChangeMutation,
} from '../../__generated__/graphql';
import { useConfirmation } from '../core/ConfirmationDialog';
import { Title } from '../core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import { RequestedHouseholdDataChangeTable } from './RequestedHouseholdDataChangeTable/RequestedHouseholdDataChangeTable';

export function RequestedHouseholdDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketNode;
  canApproveDataChange: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
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
          {t('Approve')}
        </Button>
      );
    }
    return (
      <Button
        onClick={() =>
          confirm({
            title: t('Warning'),
            content: getConfirmationText(values),
          }).then(() => {
            submitForm();
          })
        }
        variant='contained'
        color='primary'
        disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
      >
        {t('Approve')}
      </Button>
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
          const sum = Object.values(values).flat().length;
          setEdit(sum === 0);
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => (
        <ApproveBox>
          <Title>
            <Box display='flex' justifyContent='space-between'>
              <Typography variant='h6'>{t('Requested Data Change')}</Typography>
              {shouldShowEditButton(values) ? (
                <Button
                  onClick={() => setEdit(true)}
                  variant='outlined'
                  color='primary'
                  disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
                >
                  {t('EDIT')}
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
        </ApproveBox>
      )}
    </Formik>
  );
}
