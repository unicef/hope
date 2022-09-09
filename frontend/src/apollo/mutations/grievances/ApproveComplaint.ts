import { gql } from 'apollo-boost';

export const ApproveComplaint = gql`
  mutation ApproveComplaint($grievanceTicketId: ID!, $approveStatus: Boolean!) {
    approveComplaint(
      grievanceTicketId: $grievanceTicketId
      approveStatus: $approveStatus
    ) {
      grievanceTicket {
        id
        status
      }
    }
  }
`;
