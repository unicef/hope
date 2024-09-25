import { gql } from '@apollo/client';

export const ApprovePaymentDetails = gql`
  mutation ApprovePaymentDetails(
    $grievanceTicketId: ID!
    $approveStatus: Boolean!
  ) {
    approvePaymentDetails(
      grievanceTicketId: $grievanceTicketId
      approveStatus: $approveStatus
    ) {
      grievanceTicket {
        id
        status
        paymentVerificationTicketDetails {
          id
          approveStatus
        }
      }
    }
  }
`;
