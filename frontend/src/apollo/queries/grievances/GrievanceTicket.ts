import { gql } from '@apollo/client';

export const GrievanceTicket = gql`
  query GrievanceTicket($id: ID!) {
    grievanceTicket(id: $id) {
      ...grievanceTicketDetailed
    }
  }
`;
