import { useSnackbar } from '@hooks/useSnackBar';
import { useConfirmation } from '@core/ConfirmationDialog';
import { useProgramContext } from '../../programContext';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { GrievanceHouseholdDataChangeApprove } from '@restgenerated/models/GrievanceHouseholdDataChangeApprove';
import { RestService } from '@restgenerated/services/RestService';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { camelCase } from 'lodash';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import { Title } from '@core/Title';
import RequestedHouseholdDataChangeTable from './RequestedHouseholdDataChangeTable/RequestedHouseholdDataChangeTable';
import { Box, Button, Typography } from '@mui/material';
import { Formik } from 'formik';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function RequestedHouseholdDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketDetail;
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirmation = useConfirmation();
  const { isActiveProgram } = useProgramContext();
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();

  const getConfirmationText = (vals): string => {
    const allSelected =
      vals.selectedRoles.length +
        vals.selected.length +
        vals.selectedFlexFields.length || 0;
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
      const formData: GrievanceHouseholdDataChangeApprove = {
        householdApproveData,
        flexFieldsApproveData,
      };

      return RestService.restBusinessAreasGrievanceTicketsApproveHouseholdDataChangeCreate(
        {
          businessAreaSlug: businessArea,
          id: ticket.id,
          formData,
        },
      );
    },
    onSuccess: () => {
      showMessage('Changes Approved');
      queryClient.invalidateQueries({
        queryKey: ['GrievanceTicketDetail', ticket.id],
      });
    },
    onError: (err: any) => {
      if (err?.body?.errors) {
        Object.values(err.body.errors)
          .flat()
          .forEach((msg: string) => {
            showMessage(msg);
          });
      } else {
        showMessage(err?.message || 'An error occurred');
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
    ([, val]: [string, { approveStatus: boolean }]) => val.approveStatus,
  ).length;
  allApprovedCount += flexFieldsEntries.filter(
    ([, val]: [string, { approveStatus: boolean }]) => val.approveStatus,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);
  const shouldShowEditButton = (vals): boolean =>
    (vals.selected.length || vals.selectedFlexFields.length) &&
    !isEdit &&
    ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;

  const areAllApproved = (vals): boolean => {
    const selectedCount =
      vals.selected.length +
      vals.selectedFlexFields.length +
      vals.selectedRoles.length;
    const countAll = entries.length + flexFieldsEntries.length;
    return selectedCount === countAll;
  };

  const getApprovalButton = (vals, submitForm): ReactElement => {
    if (areAllApproved(vals)) {
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
          confirmation({
            title: t('Warning'),
            content: getConfirmationText(vals),
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
  const initialValues = React.useMemo(
    () => ({
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
      selectedRoles: (ticket.ticketDetails.householdData.roles || [])
        .filter((role) => role.approveStatus)
        .map((role) => role.individualId),
    }),
    [entries, flexFieldsEntries, ticket.ticketDetails.householdData.roles],
  );

  return (
    <Formik
      initialValues={initialValues}
      enableReinitialize={true}
      onSubmit={async (values) => {
        // Build householdApproveData as a flat object
        const householdApproveData: { [key: string]: boolean | any } = {};
        // Top-level fields
        entries.forEach(([key]) => {
          if (key !== 'roles' && key !== 'flexFields') {
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
        // Only add flex_fields to householdApproveData if not empty
        if (Object.keys(flexFieldsApproveData).length > 0) {
          householdApproveData.flex_fields = flexFieldsApproveData;
        } else if ('flex_fields' in householdApproveData) {
          delete householdApproveData.flex_fields;
        }
        // Roles
        const allRolesRaw = ticket.ticketDetails.householdData.roles || [];
        // Convert all role keys to camelCase for consistency
        const allRoles = allRolesRaw.map((role) =>
          Object.fromEntries(
            Object.entries(role).map(([k, v]) => [camelCase(k), v]),
          ),
        );
        householdApproveData.roles = allRoles.map((role) => ({
          individual_id: role.individualId,
          approve_status: Boolean(
            values.selectedRoles.includes(role.individualId),
          ),
        }));

        // Build mutation payload
        const mutationPayload: {
          householdApproveData: any;
        } = {
          householdApproveData,
        };

        try {
          await mutate(mutationPayload);
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
