import { gql } from 'apollo-boost';
export const REASSIGN_ROLE = gql`
  mutation ReassignRoleGrievance(
    $grievanceTicketId: ID!
    $householdId: ID!
    $individualId: ID!
    $newIndividualId: ID
    $role: String!
  ) {
    reassignRole(
      grievanceTicketId: $grievanceTicketId
      householdId: $householdId
      individualId: $individualId
      newIndividualId: $newIndividualId
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
