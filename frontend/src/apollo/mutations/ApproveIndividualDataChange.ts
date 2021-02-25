import { gql } from 'apollo-boost';
export const ApproveIndividualDataChange = gql`
  mutation ApproveIndividualDataChange(
    $grievanceTicketId: ID!
    $individualApproveData: JSONString
    $flexFieldsApproveData: JSONString
    $approvedDocumentsToCreate: [Int]
    $approvedDocumentsToRemove: [Int]
  ) {
    approveIndividualDataChange(
      grievanceTicketId: $grievanceTicketId
      individualApproveData: $individualApproveData
      flexFieldsApproveData: $flexFieldsApproveData
      approvedDocumentsToCreate: $approvedDocumentsToCreate
      approvedDocumentsToRemove: $approvedDocumentsToRemove
    ) {
      grievanceTicket {
        id
        status
        individualDataUpdateTicketDetails {
          id
          individual {
            ...individualDetailed
          }
          individualData
        }
      }
    }
  }
`;
