import { gql } from '@apollo/client';

export const RelatedGrievanceTickets = gql`
  query RelatedGrievanceTickets($id: ID!) {
    grievanceTicket(id: $id) {
      relatedTickets {
        id
        status
        category
        issueType
        unicefId
      }
    }
  }
`;
