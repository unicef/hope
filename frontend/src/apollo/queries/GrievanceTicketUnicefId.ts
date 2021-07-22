import { gql } from 'apollo-boost';

export const GrievanceTicketUnicefId = gql`
  query GrievanceTicketUnicefId($id: ID!) {
    grievanceTicket(id: $id) {
      id
      unicefId
    }
  }
`;
