import { Box, Button, Typography } from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  GrievanceTicketQuery,
  useApproveHouseholdDataChangeMutation,
} from '@generated/graphql';
import { useSnackbar } from '@hooks/useSnackBar';
import { useProgramContext } from '../../programContext';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { useConfirmation } from '@core/ConfirmationDialog';
import { Title } from '@core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import RequestedHouseholdDataChangeTable from './RequestedHouseholdDataChangeTable/RequestedHouseholdDataChangeTable';

export function RequestedHouseholdDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const { isActiveProgram } = useProgramContext();

  const getConfirmationText = (values): string => {
    const allSelected =
      values.selectedRoles.length +
        values.selected.length +
        values.selectedFlexFields.length || 0;
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
      values.selected.length +
      values.selectedFlexFields.length +
      values.selectedRoles.length;
    const countAll = entries.length + flexFieldsEntries.length;
    return selectedCount === countAll;
  };

  const getApprovalButton = (values, submitForm): ReactElement => {
    if (areAllApproved(values)) {
      return (
        <Button
          onClick={submitForm}
          variant="contained"
          color="primary"
          data-cy="button-approve"
          disabled={
            ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
            !isActiveProgram
          }
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
        variant="contained"
        color="primary"
        data-cy="button-approve"
        title={t(
          'Program has to be active to create a Linked Ticket to Feedback',
        )}
        disabled={
          ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL ||
          !isActiveProgram
        }
      >
        {t('Approve')}
      </Button>
    );
  };
  return (
    <Formik
      initialValues={{
        selected: entries
          .filter(
            (row: [string, { approve_status: boolean }]) =>
              row[1].approve_status,
          )
          .map((row) => row[0]),
        selectedFlexFields: flexFieldsEntries
          .filter(
            (row: [string, { approve_status: boolean }]) =>
              row[1].approve_status,
          )
          .map((row) => row[0]),
        selectedRoles: (
          ticket.householdDataUpdateTicketDetails.householdData.roles || []
        )
          .filter((role) => role.approve_status)
          .map((role) => role.individual_id),
      }}
      onSubmit={async (values) => {
        console.log('values1', values);
        // Build householdApproveData as a flat object
        const householdApproveData: { [key: string]: boolean | any } = {};
        // Top-level fields
        entries.forEach(([key]) => {
          if (key !== 'roles' && key !== 'flex_fields') {
            householdApproveData[key] = values.selected.includes(key);
          }
        });
        // Flex fields
        const flexFieldsApproveData: { [key: string]: boolean } = {};
        flexFieldsEntries.forEach(([key]) => {
          if (typeof flexFields[key] === 'object' && flexFields[key] !== null) {
            flexFieldsApproveData[key] =
              values.selectedFlexFields.includes(key);
          }
        });
        // Roles
        const allRoles =
          ticket.householdDataUpdateTicketDetails.householdData.roles || [];
        householdApproveData.roles = allRoles.map((role) => ({
          individual_id: role.individual_id,
          approve_status: values.selectedRoles.includes(role.individual_id),
        }));

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
            <Box display="flex" justifyContent="space-between">
              <Typography variant="h6">Requested Data Change</Typography>
              {shouldShowEditButton(values) ? (
                <Button
                  onClick={() => setEdit(true)}
                  variant="outlined"
                  color="primary"
                  data-cy="button-edit"
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
