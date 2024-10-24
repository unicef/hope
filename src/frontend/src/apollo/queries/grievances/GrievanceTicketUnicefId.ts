import { gql } from '@apollo/client';

export const GrievanceTicketUnicefId = gql`
  query GrievanceTicketUnicefId($id: ID!) {
    grievanceTicket(id: $id) {
      id
      unicefId
    }
  }
`;
