import { Box, Button, Grid2 as Grid, Typography } from '@mui/material';
import snakeCase from 'lodash/snakeCase';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useConfirmation } from '@core/ConfirmationDialog';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { Individual } from '@restgenerated/models/Individual';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { showApiErrorMessages } from '@utils/utils';

export type RoleReassignData = {
  role: string;
  individual: Individual;
  household: HouseholdDetail;
};

export function DeleteIndividualGrievanceDetails({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketDetail;
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const isHeadOfHousehold =
    ticket?.individual?.id === ticket?.household?.headOfHousehold?.id;
  const isOneIndividual = ticket?.household?.activeIndividualsCount === 1;
  const primaryCollectorRolesCount =
    ticket?.individual?.rolesInHouseholds.filter((el) => el.role === 'PRIMARY')
      .length + (isHeadOfHousehold ? 1 : 0);
  const primaryColletorRolesReassignedCount = Object.values(
    ticket.ticketDetails.roleReassignData,
  )?.filter(
    (el: RoleReassignData) => el.role === 'PRIMARY' || el.role === 'HEAD',
  ).length;

  const approveEnabled = (): boolean => {
    if (isOneIndividual && isForApproval) {
      return true;
    }
    if (
      isForApproval &&
      primaryCollectorRolesCount === primaryColletorRolesReassignedCount
    ) {
      return true;
    }
    return false;
  };

  const { businessArea } = useBaseUrl();
  const queryClient = useQueryClient();

  const { data: addIndividualFieldsData, isLoading } = useQuery({
    queryKey: ['allAddIndividualsFieldsAttributes', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsAllAddIndividualsFieldsAttributesList(
        {
          businessAreaSlug: businessArea,
        },
      ),
  });

  const mutation = useMutation({
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
  if (isLoading) return <LoadingComponent />;
  if (!addIndividualFieldsData) return null;
  const documents = ticket.individual?.documents;
  //@ts-ignore
  const fieldsDict = addIndividualFieldsData?.reduce(
    (previousValue, currentValue) => ({
      ...previousValue,
      [currentValue?.name]: currentValue,
    }),
    {},
  );

  const excludedFields = [
    'household',
    'documents',
    'rolesInHouseholds',
    'identities',
    'headingHousehold',
    'flexFields',
    'id',
    'sanctionListLastCheck',
    'createdAt',
    'updatedAt',
    'typeName',
    'commsDisability',
  ];

  const labels =
    Object.entries(ticket.individual || {})
      .filter(([key]) => {
        const snakeKey = snakeCase(key);
        const fieldAttribute = fieldsDict[snakeKey];
        return fieldAttribute && !excludedFields.includes(key);
      })
      .map(([key, value]) => {
        let textValue = value;
        const snakeKey = snakeCase(key);
        const fieldAttribute = fieldsDict[snakeKey];

        if (
          fieldAttribute?.type === 'SELECT_MANY' ||
          fieldAttribute?.type === 'SELECT_ONE'
        ) {
          if (value instanceof Array) {
            textValue = value
              .map(
                (choice) =>
                  fieldAttribute.choices.find((item) => item.value === choice)
                    ?.labelEn || '-',
              )
              .join(', ');
          } else {
            textValue = textValue === 'A_' ? null : textValue;
            textValue = textValue
              ? fieldAttribute.choices.find((item) => item.value === textValue)
                  ?.labelEn
              : '-';
          }
        }
        if (fieldAttribute?.type === 'DATE') {
          textValue = <UniversalMoment>{textValue as string}</UniversalMoment>;
        }
        return (
          <Grid key={key} size={{ xs: 6 }}>
            <LabelizedField
              label={
                snakeKey === 'sex' ? t('GENDER') : snakeKey.replace(/_/g, ' ')
              }
              value={<>{textValue}</>}
            />
          </Grid>
        );
      }) || [];

  const documentLabels =
    documents?.map((doc) => {
      const item = doc;
      return (
        <Grid key={item.country + item.type.label} size={{ xs: 6 }}>
          <LabelizedField
            label={item.type.label.replace(/_/g, ' ')}
            value={item.documentNumber}
          />
        </Grid>
      );
    }) || [];
  const allLabels = [...labels, ...documentLabels];

  let dialogText = t(
    `You did not approve the following ${beneficiaryGroup?.memberLabel} to be withdrawn. Are you sure you want to continue?`,
  );
  if (!ticket.ticketDetails.approveStatus) {
    dialogText = t(
      `You are approving the following ${beneficiaryGroup?.memberLabel} to be withdrawn. Are you sure you want to continue?`,
    );
  }
  return (
    <ApproveBox>
      <Title>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            {t(`${beneficiaryGroup?.memberLabel} to be withdrawn`)}
          </Typography>
          {canApproveDataChange && (
            <Button
              data-cy="button-approve"
              onClick={() =>
                confirm({
                  title: t('Warning'),
                  content: dialogText,
                }).then(async() => {
                  try {
                    await mutation.mutateAsync({
                      grievanceTicketId: ticket.id,
                      approveStatus: !ticket.ticketDetails?.approveStatus,
                    });
                    if (ticket.ticketDetails.approveStatus) {
                      showMessage(t('Changes Disapproved'));
                    }
                    if (!ticket.ticketDetails.approveStatus) {
                      showMessage(t('Changes Approved'));
                    }
                  } catch (error) {
                    showApiErrorMessages(error, showMessage);
                  }
                })
              }
              variant={
                ticket.ticketDetails?.approveStatus ? 'outlined' : 'contained'
              }
              color="primary"
              disabled={!approveEnabled}
            >
              {ticket.ticketDetails?.approveStatus
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
