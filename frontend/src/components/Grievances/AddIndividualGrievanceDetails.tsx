import { Box, Button, Grid, Paper, Typography } from '@material-ui/core';
import styled from 'styled-components';
import React from 'react';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useAllAddIndividualFieldsQuery,
  useApproveAddIndividualDataChangeMutation,
  useApproveIndividualDataChangeMutation,
} from '../../__generated__/graphql';
import { LabelizedField } from '../LabelizedField';
import { Formik } from 'formik';
import { ConfirmationDialog } from '../ConfirmationDialog';
import { GRIEVANCE_TICKET_STATES } from '../../utils/constants';
import { useSnackbar } from '../../hooks/useSnackBar';

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
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const { data, loading } = useAllAddIndividualFieldsQuery();
  const { showMessage } = useSnackbar();
  const [mutate] = useApproveAddIndividualDataChangeMutation();
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
  const { documents } = ticket.addIndividualTicketDetails?.individualData;
  // eslint-disable-next-line no-param-reassign
  delete ticket.addIndividualTicketDetails?.individualData.documents;
  const labels =
    Object.entries(ticket.addIndividualTicketDetails?.individualData || {}).map(
      ([key, value]) => {
        let textValue = value;
        const fieldAttribute = fieldsDict[key];
        if (fieldAttribute.type === 'SELECT_ONE') {
          textValue = fieldAttribute.choices.find(
            (item) => item.value === value,
          ).labelEn;
        }
        return (
          <Grid key={key} item xs={6}>
            <LabelizedField label={key.replace(/_/g, ' ')} value={textValue} />
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
  const allLabels = [...labels, ...documentLabels];
  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Individual Data</Typography>
          <ConfirmationDialog title='Warning' content='Are you sure?'>
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
                variant='contained'
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
        </Box>
      </Title>
      <Grid container spacing={6}>
        {allLabels}
      </Grid>
    </StyledBox>
  );
}
