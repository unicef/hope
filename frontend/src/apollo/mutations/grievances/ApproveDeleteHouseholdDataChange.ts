import { gql } from 'apollo-boost';
export const ApproveDeleteHouseholdDataChange = gql`
  mutation ApproveDeleteHouseholdDataChange(
    $grievanceTicketId: ID!
    $approveStatus: Boolean!
    $reasonHhId: String
  ) {
    approveDeleteHousehold(
      grievanceTicketId: $grievanceTicketId
      approveStatus: $approveStatus
      reasonHhId: $reasonHhId
    ) {
      grievanceTicket {
        id
        status
      }
    }
  }
`;
