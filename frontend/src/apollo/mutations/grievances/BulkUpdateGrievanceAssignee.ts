import { gql } from 'apollo-boost';
export const Bulk_Update_Grievance_Tickets_Assignees_Mutation = gql`
  mutation BulkUpdateGrievanceAssignee(
    $grievanceTicketUnicefIds: [ID]
    $assignedTo: String
    $businessAreaSlug: String!
  ) {
    bulkUpdateGrievanceAssignee(
      grievanceTicketUnicefIds: $grievanceTicketUnicefIds
      assignedTo: $assignedTo
      businessAreaSlug: $businessAreaSlug
    ) {
      grievanceTickets {
        assignedTo {
          firstName
          lastName
          email
        }
      }
    }
  }
`;
