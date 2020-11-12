import { gql } from 'apollo-boost';
export const GRIEVANCE_STATUS_CHANGE = gql`
  mutation GrievanceStatusChange($grievanceTicketId: ID, $status: Int) {
    grievanceStatusChange(
      grievanceTicketId: $grievanceTicketId
      status: $status
    ) {
      grievanceTicket {
        id
        status
        createdAt
        updatedAt
        createdBy {
          firstName
          lastName
          username
          email
        }
      }
    }
  }
`;
