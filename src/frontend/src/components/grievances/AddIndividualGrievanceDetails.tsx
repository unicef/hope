import { Box, Button, Grid2 as Grid, Typography } from '@mui/material';
import capitalize from 'lodash/capitalize';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import {
  getFlexFieldTextValue,
  renderBoolean,
  showApiErrorMessages,
} from '@utils/utils';
import { useConfirmation } from '@core/ConfirmationDialog';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import { useProgramContext } from 'src/programContext';
import { ReactElement, ReactNode } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';

function AddIndividualGrievanceDetails({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketDetail;
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const queryClient = useQueryClient();

  const { data, isLoading: loading } = useQuery({
    queryKey: ['addIndividualFieldsAttributes', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllAddIndividualsFieldsAttributesList(
        {
          businessAreaSlug: businessArea,
        },
      ),
  });

  const { mutateAsync } = useMutation({
    mutationFn: ({
      grievanceTicketId,
      approveStatus,
    }: {
      grievanceTicketId: string;
      approveStatus: boolean;
    }) =>
      RestService.restBusinessAreasGrievanceTicketsApproveStatusUpdateCreate({
        businessAreaSlug: businessArea,
        id: grievanceTicketId,
        formData: {
          approveStatus,
        },
      }),
    onSuccess: () => {
      // Invalidate and refetch the grievance ticket details
      queryClient.invalidateQueries({
        queryKey: ['grievanceTicket', ticket.id],
      });
    },
  });
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const confirm = useConfirmation();
  const { showMessage } = useSnackbar();
  if (loading) {
    return <LoadingComponent />;
  }
  if (!data) {
    return null;
  }
  const fieldsDict =
    data?.results?.reduce(
      (previousValue, currentValue) => ({
        ...previousValue,
        [currentValue?.name]: currentValue,
      }),
      {},
    ) || {};

  const individualData = {
    ...ticket.ticketDetails?.individualData,
  };
  const documents = individualData?.documents;
  const identities = individualData?.identities;
  delete individualData.documents;
  delete individualData.identities;
  const flexFields = individualData?.flexFields;
  delete individualData?.flexFields;
  delete individualData.documents;
  delete individualData.identities;
  const labels =
    Object.entries(individualData || {}).map(([key, value]) => {
      let textValue = value;

      const fieldAttribute = fieldsDict[key];
      if (fieldAttribute.type === 'BOOL') {
        textValue = renderBoolean(value as boolean);
      }
      if (fieldAttribute.type === 'SELECT_ONE') {
        textValue =
          fieldAttribute.choices.find((item) => item.value === value)
            ?.labelEn || '-';
      }
      if (Array.isArray(value)) {
        textValue = value.map((el) => capitalize(el)).join(', ');
      }
      return (
        <Grid key={key} size={{ xs: 6 }}>
          <LabelizedField
            label={key === 'sex' ? t('GENDER') : key.replace(/_/g, ' ')}
            value={<span>{textValue as ReactNode}</span>}
          />
        </Grid>
      );
    }) || [];

  const flexFieldLabels =
    Object.entries(flexFields || {}).map(
      ([key, value]: [string, string | string[]]) => (
        <Grid key={key} size={{ xs: 6 }}>
          <LabelizedField
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
            value={getFlexFieldTextValue(key, value, fieldsDict[key])}
          />
        </Grid>
      ),
    ) || [];
  const documentLabels =
    documents?.map((item) => (
      <Grid key={item?.country + item?.key} size={{ xs: 6 }}>
        <LabelizedField
          label={item?.key?.replace(/_/g, ' ')}
          value={item.number}
        />
      </Grid>
    )) || [];
  const identityLabels =
    identities?.map((item) => {
      const partner = item.partner || item.agency; // For backward compatibility
      return (
        <Grid key={item.country + partner} size={{ xs: 6 }}>
          <LabelizedField label={partner} value={item.number} />
        </Grid>
      );
    }) || [];
  const allLabels = [
    ...labels,
    ...flexFieldLabels,
    ...documentLabels,
    ...identityLabels,
  ];

  let dialogText = t(
    `You did not approve the following add ${beneficiaryGroup?.memberLabel} data. Are you sure you want to continue?`,
  );
  if (!ticket.ticketDetails.approveStatus) {
    dialogText = t(
      `You are approving the following Add ${beneficiaryGroup?.memberLabel} data. Are you sure you want to continue?`,
    );
  }

  return (
    <ApproveBox>
      <Title>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            {t(`${beneficiaryGroup?.memberLabel} Data`)}
          </Typography>
          {canApproveDataChange && (
            <Button
              data-cy="button-approve"
              onClick={async () => {
                try {
                  await confirm({
                    title: t('Warning'),
                    content: dialogText,
                  });
                  await mutateAsync({
                    grievanceTicketId: ticket.id,
                    approveStatus: !ticket.ticketDetails.approveStatus,
                  });
                  if (ticket.ticketDetails.approveStatus) {
                    showMessage(t('Changes Disapproved'));
                  }
                  if (!ticket.ticketDetails.approveStatus) {
                    showMessage(t('Changes Approved'));
                  }
                } catch (e) {
                  showApiErrorMessages(e, showMessage);
                }
              }}
              variant={
                ticket.ticketDetails?.approveStatus ? 'outlined' : 'contained'
              }
              color="primary"
              disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
            >
              {ticket.ticketDetails.approveStatus
                ? t('Disapprove')
                : t('Approve')}
            </Button>
          )}
        </Box>
      </Title>
      <Grid container spacing={6}>
        {allLabels}
      </Grid>
    </ApproveBox>
  );
}
export default withErrorBoundary(
  AddIndividualGrievanceDetails,
  'AddIndividualGrievanceDetails',
);
