import { gql } from '@apollo/client';
export const ApproveDeleteIndividualDataChange = gql`
  mutation ApproveSystemFlagging(
    $grievanceTicketId: ID!
    $approveStatus: Boolean!
  ) {
    approveSystemFlagging(
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
