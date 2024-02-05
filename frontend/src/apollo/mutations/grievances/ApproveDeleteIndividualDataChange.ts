import { gql } from '@apollo/client';
export const ApproveDeleteIndividualDataChange = gql`
  mutation ApproveDeleteIndividualDataChange(
    $grievanceTicketId: ID!
    $approveStatus: Boolean!
  ) {
    approveDeleteIndividual(
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
