import { gql } from 'apollo-boost';
export const REASSIGN_ROLE = gql`
  mutation ReassignRole(
    $grievanceTicketId: ID!
    $householdId: ID!
    $individualId: ID!
    $role: String!
  ) {
    reassignRole(
      grievanceTicketId: $grievanceTicketId
      householdId: $householdId
      individualId: $individualId
      role: $role
    ) {
      household {
        id
        unicefId
      }
      individual {
        id
        unicefId
      }
    }
  }
`;
