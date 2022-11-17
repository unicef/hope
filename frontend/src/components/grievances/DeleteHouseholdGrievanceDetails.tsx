import { Box, Button, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useSnackbar } from '../../hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { choicesToDict } from '../../utils/utils';
import {
  GrievanceTicketDocument,
  GrievanceTicketNode,
  useApproveDeleteHouseholdDataChangeMutation,
  useHouseholdChoiceDataQuery,
} from '../../__generated__/graphql';
import { useConfirmation } from '../core/ConfirmationDialog';
import { ContentLink } from '../core/ContentLink';
import { LabelizedField } from '../core/LabelizedField';
import { LoadingComponent } from '../core/LoadingComponent';
import { Title } from '../core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';

export const DeleteHouseholdGrievanceDetails = ({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketNode;
  canApproveDataChange: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate] = useApproveDeleteHouseholdDataChangeMutation();
  const confirm = useConfirmation();
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const approveEnabled = isForApproval;

  let dialogText = t(
    'You did not approve the following household to be withdrawn. Are you sure you want to continue?',
  );
  if (!ticket.deleteHouseholdTicketDetails.approveStatus) {
    dialogText = t(
      'You are approving the following household to be withdrawn. Are you sure you want to continue?',
    );
  }
  if (choicesLoading) return <LoadingComponent />;

  const residenceChoicesDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );

  return (
    <ApproveBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Household to be withdrawn')}</Typography>
          {canApproveDataChange && (
            <Button
              onClick={() =>
                confirm({
                  title: t('Warning'),
                  content: dialogText,
                }).then(async () => {
                  try {
                    await mutate({
                      variables: {
                        grievanceTicketId: ticket.id,
                        approveStatus: !ticket.deleteHouseholdTicketDetails
                          ?.approveStatus,
                      },
                      refetchQueries: () => [
                        {
                          query: GrievanceTicketDocument,
                          variables: { id: ticket.id },
                        },
                      ],
                    });
                    if (ticket.deleteHouseholdTicketDetails.approveStatus) {
                      showMessage(t('Changes Disapproved'));
                    }
                    if (!ticket.deleteHouseholdTicketDetails.approveStatus) {
                      showMessage(t('Changes Approved'));
                    }
                  } catch (e) {
                    e.graphQLErrors.map((x) => showMessage(x.message));
                  }
                })
              }
              variant={
                ticket.deleteHouseholdTicketDetails?.approveStatus
                  ? 'outlined'
                  : 'contained'
              }
              color='primary'
              disabled={!approveEnabled}
            >
              {ticket.deleteHouseholdTicketDetails?.approveStatus
                ? t('Disapprove')
                : t('Approve')}
            </Button>
          )}
        </Box>
      </Title>
      <Grid container spacing={6}>
        <Grid item xs={3}>
          <LabelizedField label={t('Household Size')}>
            {ticket.household.size}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Residence Status')}>
            {residenceChoicesDict[ticket.household.residenceStatus]}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Head of Household')}>
            <ContentLink
              href={`/${businessArea}/population/individuals/${ticket.household.headOfHousehold.id}`}
            >
              {ticket.household.headOfHousehold.fullName}
            </ContentLink>
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Country')}>
            {ticket.household.country}
          </LabelizedField>
        </Grid>

        <Grid item xs={3}>
          <LabelizedField label={t('Country of Origin')}>
            {ticket.household.countryOrigin}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Address')}>
            {ticket.household.address}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Village')}>
            {ticket.household.village}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 1')}>
            {ticket.household.admin1?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Administrative Level 2')}>
            {ticket.household.admin2?.name}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Geolocation')}>
            {ticket.household.geopoint
              ? `${ticket.household.geopoint.coordinates[0]}, ${ticket.household.geopoint.coordinates[1]}`
              : '-'}
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('UNHCR CASE ID')}>
            {ticket.household?.unhcrId}
          </LabelizedField>
        </Grid>
      </Grid>
    </ApproveBox>
  );
};
