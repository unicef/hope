import { gql } from 'apollo-boost';
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
