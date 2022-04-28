import { gql } from 'apollo-boost';

export const ApproveDeleteIndividualDataChange = gql`
  mutation ApproveNeedsAdjudication(
    $grievanceTicketId: ID!
    $selectedIndividualId: ID
  ) {
    approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId
      selectedIndividualId: $selectedIndividualId
    ) {
      grievanceTicket {
        id
        status
      }
    }
  }
`;
