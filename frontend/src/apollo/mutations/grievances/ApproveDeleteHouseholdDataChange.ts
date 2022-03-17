import { gql } from 'apollo-boost';
export const ApproveDeleteHouseholdDataChange = gql`
  mutation ApproveDeleteHouseholdDataChange(
    $grievanceTicketId: ID!
    $approveStatus: Boolean!
  ) {
    approveDeleteHousehold(
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
