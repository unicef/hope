import { Box, Button, Grid, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React from 'react';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
  useApproveAddIndividualDataChangeMutation,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { useSnackbar } from '../../hooks/useSnackBar';
import { getFlexFieldTextValue, renderBoolean } from '../../utils/utils';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function AddIndividualGrievanceDetails({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): React.ReactElement {
  const { data, loading } = useAllAddIndividualFieldsQuery();
  const [mutate] = useApproveAddIndividualDataChangeMutation();
  const { showMessage } = useSnackbar();
  if (loading) {
    return null;
  }
  const fieldsDict = data.allAddIndividualsFieldsAttributes.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.name] = currentValue;
      return previousValue;
    },
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
        textValue = fieldAttribute.choices.find((item) => item.value === value)
          .labelEn;
      }
      return (
        <Grid key={key} item xs={6}>
          <LabelizedField
            label={key === 'sex' ? 'GENDER' : key.replace(/_/g, ' ')}
            value={textValue}
          />
        </Grid>
      );
    }) || [];
  const flexFieldLabels =
    Object.entries(flexFields || {}).map(
      ([key, value]: [string, string | string[]]) => {
        return (
          <Grid key={key} item xs={6}>
            <LabelizedField
              label={key.replaceAll('_i_f', '').replace(/_/g, ' ')}
              value={getFlexFieldTextValue(key, value, fieldsDict[key])}
            />
          </Grid>
        );
      },
    ) || [];
  const documentLabels =
    documents?.map((item) => {
      return (
        <Grid key={item.country + item.type} item xs={6}>
          <LabelizedField
            label={item.type.replace(/_/g, ' ')}
            value={item.number}
          />
        </Grid>
      );
    }) || [];
  const identityLabels =
    identities?.map((item) => {
      return (
        <Grid key={item.country + item.agency} item xs={6}>
          <LabelizedField label={item.agency} value={item.number} />
        </Grid>
      );
    }) || [];
  const allLabels = [
    ...labels,
    ...flexFieldLabels,
    ...documentLabels,
    ...identityLabels,
  ];

  let dialogText =
    'You did not approve the following add individual data. Are you sure you want to continue?';
  if (!ticket.addIndividualTicketDetails.approveStatus) {
    dialogText =
      'You are approving the following Add individual data. Are you sure you want to continue?';
  }

  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Individual Data</Typography>
          {canApproveDataChange && (
            <ConfirmationDialog title='Warning' content={dialogText}>
              {(confirm) => (
                <Button
                  onClick={confirm(async () => {
                    try {
                      await mutate({
                        variables: {
                          grievanceTicketId: ticket.id,
                          approveStatus: !ticket.addIndividualTicketDetails
                            .approveStatus,
                        },
                        refetchQueries: () => [
                          {
                            query: GrievanceTicketDocument,
                            variables: { id: ticket.id },
                          },
                        ],
                      });
                      if (ticket.addIndividualTicketDetails.approveStatus) {
                        showMessage('Changes Disapproved');
                      }
                      if (!ticket.addIndividualTicketDetails.approveStatus) {
                        showMessage('Changes Approved');
                      }
                    } catch (e) {
                      e.graphQLErrors.map((x) => showMessage(x.message));
                    }
                  })}
                  variant={
                    ticket.addIndividualTicketDetails?.approveStatus
                      ? 'outlined'
                      : 'contained'
                  }
                  color='primary'
                  disabled={
                    ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                  }
                >
                  {ticket.addIndividualTicketDetails.approveStatus
                    ? 'Disapprove'
                    : 'Approve'}
                </Button>
              )}
            </ConfirmationDialog>
          )}
        </Box>
      </Title>
      <Grid container spacing={6}>
        {allLabels}
      </Grid>
    </StyledBox>
  );
}
