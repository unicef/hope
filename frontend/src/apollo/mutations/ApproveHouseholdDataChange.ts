import {gql} from 'apollo-boost';

export const ApproveHouseholdDataChange = gql`
  mutation ApproveHouseholdDataChange(
    $grievanceTicketId: ID!
    $householdApproveData: JSONString
    $flexFieldsApproveData: JSONString
  ) {
    approveHouseholdDataChange(
      grievanceTicketId: $grievanceTicketId
      householdApproveData: $householdApproveData
      flexFieldsApproveData: $flexFieldsApproveData
    ) {
      grievanceTicket {
        id
        status
        householdDataUpdateTicketDetails {
          id
          household {
            ...householdDetailed
          }
          householdData
        }
      }
    }
  }
`;
