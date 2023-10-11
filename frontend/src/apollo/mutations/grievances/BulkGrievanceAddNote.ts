import { gql } from 'apollo-boost';
export const BulkUpdateGrievanceAddNote = gql`
  mutation BulkUpdateGrievanceAddNote(
    $grievanceTicketIds: [ID]!
    $note: String!
    $businessAreaSlug: String!
  ) {
    bulkGrievanceAddNote(
      grievanceTicketIds: $grievanceTicketIds
      note: $note
      businessAreaSlug: $businessAreaSlug
    ) {
      grievanceTickets {
        id
      }
    }
  }
`;
