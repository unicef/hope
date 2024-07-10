import { gql } from '@apollo/client';

export const ApproveDeleteIndividualDataChange = gql`
  mutation ApproveNeedsAdjudication(
    $grievanceTicketId: ID!
    $selectedIndividualId: ID
    $duplicateIndividualIds: [ID]
  ) {
    approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId
      selectedIndividualId: $selectedIndividualId
      duplicateIndividualIds: $duplicateIndividualIds
    ) {
      grievanceTicket {
        id
        status
      }
    }
  }
`;
