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
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}): React.ReactElement {
  const { showMessage } = useSnackbar();
  const [mutate] = useApproveAddIndividualDataChangeMutation();

  // const documents = ticket.individual?.documents;
  // // eslint-disable-next-line no-param-reassign
  // delete ticket.addIndividualTicketDetails?.individualData.documents;
  // const labels =
  //   Object.entries(ticket.individual || {}).map(([key, value]) => {
  //     return (
  //       <Grid key={key} item xs={6}>
  //         <LabelizedField label={key.replace(/_/g, ' ')} value={value} />
  //       </Grid>
  //     );
  //   }) || [];
  // const documentLabels =
  //   documents?.edges?.map((edge) => {
  //     const item = edge.node;
  //     return (
  //       <Grid key={item.type.country + item.type.label} item xs={6}>
  //         <LabelizedField
  //           label={item.type.label.replace(/_/g, ' ')}
  //           value={item.documentNumber}
  //         />
  //       </Grid>
  //     );
  //   }) || [];
  // const allLabels = [...labels, ...documentLabels];
  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>Individual to be deleted</Typography>
          <ConfirmationDialog title='Warning' content='Are you sure?'>
            {(confirm) => (
              <Button
                onClick={() => null}
                // onClick={confirm(async () => {
                //   try {
                //     await mutate({
                //       variables: {
                //         grievanceTicketId: ticket.id,
                //         approveStatus: !ticket.addIndividualTicketDetails
                //           .approveStatus,
                //       },
                //       refetchQueries: () => [
                //         {
                //           query: GrievanceTicketDocument,
                //           variables: { id: ticket.id },
                //         },
                //       ],
                //     });
                //     if (ticket.addIndividualTicketDetails.approveStatus) {
                //       showMessage('Changes Disapproved');
                //     }
                //     if (!ticket.addIndividualTicketDetails.approveStatus) {
                //       showMessage('Changes Approved');
                //     }
                //   } catch (e) {
                //     e.graphQLErrors.map((x) => showMessage(x.message));
                //   }
                // })}
                variant='contained'
                color='primary'
                disabled={
                  ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL
                }
              >
                APPROVE
              </Button>
            )}
          </ConfirmationDialog>
        </Box>
      </Title>
      <Grid container spacing={6}>
        {/* {allLabels} */}
        table
      </Grid>
    </StyledBox>
  );
}
