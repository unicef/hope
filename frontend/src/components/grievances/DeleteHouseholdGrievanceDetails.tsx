import { Box, Button, Grid, Typography } from '@material-ui/core';
import { Field, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { choicesToDict } from '../../utils/utils';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
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
  ticket: GrievanceTicketQuery['grievanceTicket'];
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
  const dialogText = t(
    'You did not approve the following household to be withdrawn. Are you sure you want to continue?',
  );

  const dialogContentWithdrawReason = (
    <Formik
      initialValues={{ withdrawReason: '', duplicateHouseholdId: null }}
      enableReinitialize
      onSubmit={(values) => {
        console.log('VALUES', values);
      }}
    >
      {({ submitForm }) => (
        <Box display='flex' flexDirection='column'>
          <Box mt={2}>
            <Typography variant='body2'>
              {t('Please provide the reason of withdrawal of this household.')}
            </Typography>
          </Box>
          <Field
            name='withdrawReason'
            choices={[
              {
                value: 'duplicate',
                name: 'This household is a duplicate of another household',
              },
            ]}
            component={FormikRadioGroup}
            noMargin
          />
          <Grid container>
            <Grid item xs={6}>
              <Field
                name='duplicateHouseholdId'
                fullWidth
                variant='outlined'
                label={t('Household Id')}
                component={FormikTextField}
                required
              />
            </Grid>
          </Grid>
          <Field
            name='withdrawReason'
            choices={[{ value: 'other', name: 'Other' }]}
            component={FormikRadioGroup}
            noMargin
          />
          <Button onClick={submitForm}>Submit</Button>
        </Box>
      )}
    </Formik>
  );

  const { approveStatus } = ticket.deleteHouseholdTicketDetails;

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
                  title: approveStatus
                    ? t('Warning')
                    : t('Reason of withdrawal'),
                  content: approveStatus
                    ? dialogText
                    : dialogContentWithdrawReason,
                  continueText: t('Confirm'),
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
                    if (approveStatus) {
                      showMessage(t('Changes Disapproved'));
                    }
                    if (!approveStatus) {
                      showMessage(t('Changes Approved'));
                    }
                  } catch (e) {
                    e.graphQLErrors.map((x) => showMessage(x.message));
                  }
                })
              }
              variant={approveStatus ? 'outlined' : 'contained'}
              color='primary'
              disabled={!approveEnabled}
            >
              {approveStatus ? t('Disapprove') : t('Approve')}
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
