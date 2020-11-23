import { gql } from 'apollo-boost';
export const ApproveHouseholdDataChange = gql`
  mutation ApproveHouseholdDataChange(
    $grievanceTicketId: ID!
    $householdApproveData: JSONString
  ) {
    approveHouseholdDataChange(
      grievanceTicketId: $grievanceTicketId
      householdApproveData: $householdApproveData
    ) {
      grievanceTicket {
        id
        status
      }
    }
  }
`;
