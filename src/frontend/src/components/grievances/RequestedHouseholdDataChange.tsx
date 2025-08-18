import { useSnackbar } from '@hooks/useSnackBar';
import { useConfirmation } from '@core/ConfirmationDialog';
import { useProgramContext } from '../../programContext';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { GrievanceHouseholdDataChangeApprove } from '@restgenerated/models/GrievanceHouseholdDataChangeApprove';
import { RestService } from '@restgenerated/services/RestService';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
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
  const householdData = React.useMemo(
    () => ({
      ...ticket.ticketDetails.householdData,
    }),
    [ticket.ticketDetails.householdData],
  );
  // Define rolesArr in main scope
  const rolesArr = householdData.roles || [];
  let allApprovedCount = 0;
  const flexFields = householdData?.flexFields || {};
  delete householdData.flexFields;
  const flexFieldsEntries = Object.entries(flexFields);
  const entries = Object.entries(householdData);
  // Count approved top-level fields
  allApprovedCount += entries.filter(
    ([, val]: [string, { approve_status: boolean }]) => val.approve_status,
  ).length;
  // Count approved flex fields
  allApprovedCount += flexFieldsEntries.filter(
    ([, val]: [string, { approve_status: boolean }]) => val.approve_status,
  ).length;
  // Count approved roles
  allApprovedCount += rolesArr.filter(
    (role) =>
      role &&
      typeof role === 'object' &&
      'approve_status' in role &&
      role.approve_status === true,
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
  const initialValues = React.useMemo(() => {
    // Use householdData from upper scope
    // Top-level fields (exclude roles and flex_fields)
    const selected = Object.entries(householdData)
      .filter(
        ([key, val]) =>
          key !== 'roles' &&
          key !== 'flex_fields' &&
          val &&
          typeof val === 'object' &&
          'approve_status' in val &&
          (val as any).approve_status === true,
      )
      .map(([key]) => key);

    // Flex fields
    const flexFieldsObj = householdData.flex_fields || {};
    const selectedFlexFields = Object.entries(flexFieldsObj)
      .filter(
        ([, val]) =>
          val &&
          typeof val === 'object' &&
          'approve_status' in val &&
          (val as any).approve_status === true,
      )
      .map(([key]) => key);

    // Roles
    const selectedRoles = rolesArr
      .filter(
        (role) =>
          role &&
          typeof role === 'object' &&
          'approve_status' in role &&
          role.approve_status === true,
      )
      .map((role) => role.individual_id);

    return {
      selected,
      selectedFlexFields,
      selectedRoles,
    };
  }, [householdData]);

  return (
    <Formik
      initialValues={initialValues}
      enableReinitialize={true}
      onSubmit={async (values) => {
        // Build householdApproveData as a flat object
        const householdApproveData: { [key: string]: boolean | any } = {};
        // Top-level fields
        values.selected.forEach((key) => {
          householdApproveData[key] = true;
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
        // Roles: add each as roles__<individual_id>: boolean
        householdApproveData.roles = values.selectedRoles.map(
          (individualId) => ({
            individual_id: individualId,
            approve_status: true,
          }),
        );

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
