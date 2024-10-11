import { Box, Button, Grid, Typography } from '@mui/material';
import * as React from 'react';
import capitalize from 'lodash/capitalize';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { getFlexFieldTextValue, renderBoolean } from '@utils/utils';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
  useApproveAddIndividualDataChangeMutation,
} from '@generated/graphql';
import { useConfirmation } from '@core/ConfirmationDialog';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { ApproveBox } from './GrievancesApproveSection/ApproveSectionStyles';

export function AddIndividualGrievanceDetails({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const { data, loading } = useAllAddIndividualFieldsQuery();
  const [mutate] = useApproveAddIndividualDataChangeMutation();
  const confirm = useConfirmation();
  const { showMessage } = useSnackbar();
  if (loading) {
    return <LoadingComponent />;
  }
  if (!data) {
    return null;
  }
  const fieldsDict = data.allAddIndividualsFieldsAttributes.reduce(
    (previousValue, currentValue) => ({
      ...previousValue,
      [currentValue?.name]: currentValue,
    }),
    {},
  );

  const individualData = {
    ...ticket.addIndividualTicketDetails?.individualData,
  };
  const documents = individualData?.documents;
  const identities = individualData?.identities;
  delete individualData.documents;
  delete individualData.identities;
  const flexFields = individualData?.flex_fields;
  delete individualData?.flex_fields;
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
        <Grid key={key} item xs={6}>
          <LabelizedField
            label={key === 'sex' ? t('GENDER') : key.replace(/_/g, ' ')}
            value={<span>{textValue as React.ReactNode}</span>}
          />
        </Grid>
      );
    }) || [];

  const flexFieldLabels =
    Object.entries(flexFields || {}).map(
      ([key, value]: [string, string | string[]]) => (
        <Grid key={key} item xs={6}>
          <LabelizedField
            label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
            value={getFlexFieldTextValue(key, value, fieldsDict[key])}
          />
        </Grid>
      ),
    ) || [];
  const documentLabels =
    documents?.map((item) => (
      <Grid key={item?.country + item?.key} item xs={6}>
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
        <Grid key={item.country + partner} item xs={6}>
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
    'You did not approve the following add individual data. Are you sure you want to continue?',
  );
  if (!ticket.addIndividualTicketDetails.approveStatus) {
    dialogText = t(
      'You are approving the following Add individual data. Are you sure you want to continue?',
    );
  }

  return (
    <ApproveBox>
      <Title>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">{t('Individual Data')}</Typography>
          {canApproveDataChange && (
            <Button
              data-cy="button-approve"
              onClick={() =>
                confirm({
                  title: t('Warning'),
                  content: dialogText,
                }).then(async () => {
                  try {
                    await mutate({
                      variables: {
                        grievanceTicketId: ticket.id,
                        approveStatus:
                          !ticket.addIndividualTicketDetails.approveStatus,
                      },
                      refetchQueries: () => [
                        {
                          query: GrievanceTicketDocument,
                          variables: { id: ticket.id },
                        },
                      ],
                    });
                    if (ticket.addIndividualTicketDetails.approveStatus) {
                      showMessage(t('Changes Disapproved'));
                    }
                    if (!ticket.addIndividualTicketDetails.approveStatus) {
                      showMessage(t('Changes Approved'));
                    }
                  } catch (e) {
                    e.graphQLErrors.map((x) => showMessage(x.message));
                  }
                })
              }
              variant={
                ticket.addIndividualTicketDetails?.approveStatus
                  ? 'outlined'
                  : 'contained'
              }
              color="primary"
              disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
            >
              {ticket.addIndividualTicketDetails.approveStatus
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
