import React from 'react';
import snakeCase from 'lodash/snakeCase';
import { Box, Button, Grid, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
  useApproveDeleteIndividualDataChangeMutation,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { useSnackbar } from '../../hooks/useSnackBar';
import { LoadingComponent } from '../LoadingComponent';
import { UniversalMoment } from '../UniversalMoment';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export function DeleteIndividualGrievanceDetails({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canApproveDataChange: boolean;
}): React.ReactElement {
  const { showMessage } = useSnackbar();

  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const isHeadOfHousehold =
    ticket?.individual?.id === ticket?.household?.headOfHousehold?.id;
  const rolesCount =
    ticket.individual?.householdsAndRoles.length + (isHeadOfHousehold ? 1 : 0);
  const rolesReassignedCount = Object.keys(
    JSON.parse(ticket.deleteIndividualTicketDetails.roleReassignData),
  ).length;
  const approveEnabled = isForApproval && rolesCount === rolesReassignedCount;

  const { data, loading } = useAllAddIndividualFieldsQuery();
  const [mutate] = useApproveDeleteIndividualDataChangeMutation();
  if (loading) return <LoadingComponent />;
  const documents = ticket.individual?.documents;
  const fieldsDict = data.allAddIndividualsFieldsAttributes.reduce(
    (previousValue, currentValue) => {
      // eslint-disable-next-line no-param-reassign
      previousValue[currentValue.name] = currentValue;
      return previousValue;
    },
    {},
  );

  const excludedFields = [
    'household',
    'documents',
    'householdsAndRoles',
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

        if (fieldAttribute?.type === 'SELECT_ONE') {
          textValue = textValue === 'A_' ? null : textValue;
          textValue = textValue
            ? fieldAttribute.choices.find((item) => item.value === textValue)
                .labelEn
            : '-';
        }
        if (fieldAttribute?.type === 'DATE') {
          textValue = <UniversalMoment>{textValue}</UniversalMoment>;
        }
        return (
          <Grid key={key} item xs={6}>
            <LabelizedField
              label={snakeKey.replace(/_/g, ' ')}
              value={textValue}
            />
          </Grid>
        );
      }) || [];

  const documentLabels =
    documents?.edges?.map((edge) => {
      const item = edge.node;
      return (
        <Grid key={item.type.country + item.type.label} item xs={6}>
          <LabelizedField
            label={item.type.label.replace(/_/g, ' ')}
            value={item.documentNumber}
          />
        </Grid>
      );
    }) || [];
  const allLabels = [...labels, ...documentLabels];

  let dialogText =
    'You did not approve the following individual to be withdrawn. Are you sure you want to continue?';
  if (!ticket.deleteIndividualTicketDetails.approveStatus) {
    dialogText =
      'You are approving the following individual to be withdrawn. Are you sure you want to continue?';
  }
  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Individual to be withdrawn</Typography>
          {canApproveDataChange && (
            <ConfirmationDialog title='Warning' content={dialogText}>
              {(confirm) => (
                <Button
                  onClick={confirm(async () => {
                    try {
                      await mutate({
                        variables: {
                          grievanceTicketId: ticket.id,
                          approveStatus: !ticket.deleteIndividualTicketDetails
                            ?.approveStatus,
                        },
                        refetchQueries: () => [
                          {
                            query: GrievanceTicketDocument,
                            variables: { id: ticket.id },
                          },
                        ],
                      });
                      if (ticket.deleteIndividualTicketDetails.approveStatus) {
                        showMessage('Changes Disapproved');
                      }
                      if (!ticket.deleteIndividualTicketDetails.approveStatus) {
                        showMessage('Changes Approved');
                      }
                    } catch (e) {
                      e.graphQLErrors.map((x) => showMessage(x.message));
                    }
                  })}
                  variant={
                    ticket.deleteIndividualTicketDetails?.approveStatus
                      ? 'outlined'
                      : 'contained'
                  }
                  color='primary'
                  disabled={!approveEnabled}
                >
                  {ticket.deleteIndividualTicketDetails?.approveStatus
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
