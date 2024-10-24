import { gql } from '@apollo/client';

export const ApproveAddIndividualDataChange = gql`
  mutation ApproveAddIndividualDataChange(
    $grievanceTicketId: ID!
    $approveStatus: Boolean!
  ) {
    approveAddIndividual(
      grievanceTicketId: $grievanceTicketId
      approveStatus: $approveStatus
    ) {
      grievanceTicket {
        id
        status
      }
    }
  }
`;
