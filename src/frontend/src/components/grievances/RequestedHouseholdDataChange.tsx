import { Box, Button, Typography } from '@mui/material';
import { Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from '@hooks/useSnackBar';
import { useProgramContext } from '../../programContext';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { useConfirmation } from '@core/ConfirmationDialog';
import { Title } from '@core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import RequestedHouseholdDataChangeTable from './RequestedHouseholdDataChangeTable/RequestedHouseholdDataChangeTable';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { GrievanceHouseholdDataChangeApprove } from '@restgenerated/models/GrievanceHouseholdDataChangeApprove';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { camelCase } from 'lodash';

export function RequestedHouseholdDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketDetail;
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const { isActiveProgram } = useProgramContext();
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();

  const getConfirmationText = (values): string => {
    const allSelected =
      values.selected.length + values.selectedFlexFields.length || 0;
    return `You approved ${allSelected} change${
      allSelected === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };

  const { mutateAsync: mutate } = useMutation({
    mutationFn: ({
      householdApproveData,
      flexFieldsApproveData,
    }: {
      householdApproveData: any;
      flexFieldsApproveData?: any;
    }) => {
      const requestBody: GrievanceHouseholdDataChangeApprove = {
        householdApproveData,
        flexFieldsApproveData,
      };

      return RestService.restBusinessAreasGrievanceTicketsApproveHouseholdDataChangeCreate(
        {
          businessAreaSlug: businessArea,
          id: ticket.id,
          requestBody,
        },
      );
    },
    onSuccess: () => {
      showMessage('Changes Approved');
      queryClient.invalidateQueries({
        queryKey: ['GrievanceTicketDetail', ticket.id],
      });
    },
    onError: (error: any) => {
      if (error?.body?.errors) {
        Object.values(error.body.errors)
          .flat()
          .forEach((msg: string) => {
            showMessage(msg);
          });
      } else {
        showMessage(error?.message || 'An error occurred');
      }
    },
  });
  const householdData = {
    ...ticket.ticketDetails.householdData,
  };
  let allApprovedCount = 0;
  const flexFields = householdData?.flexFields || {};
  delete householdData.flexFields;
  const flexFieldsEntries = Object.entries(flexFields);
  const entries = Object.entries(householdData);
  allApprovedCount += entries.filter(
    ([, value]: [string, { approveStatus: boolean }]) => value.approveStatus,
  ).length;
  allApprovedCount += flexFieldsEntries.filter(
    ([, value]: [string, { approveStatus: boolean }]) => value.approveStatus,
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
            (row: [string, { approveStatus: boolean }]) => row[1].approveStatus,
          )
          .map((row) => camelCase(row[0])),
        selectedFlexFields: flexFieldsEntries
          .filter(
            (row: [string, { approveStatus: boolean }]) => row[1].approveStatus,
          )
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
            householdApproveData,
            flexFieldsApproveData,
          });
          const sum = Object.values(values).flat().length;
          setEdit(sum === 0);
        } catch (error) {
          // Error handling is done in the mutation's onError callback
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
