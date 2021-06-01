import { gql } from 'apollo-boost';
export const ApproveIndividualDataChange = gql`
  mutation ApproveIndividualDataChange(
    $grievanceTicketId: ID!
    $individualApproveData: JSONString
    $flexFieldsApproveData: JSONString
    $approvedDocumentsToCreate: [Int]
    $approvedDocumentsToRemove: [Int]
    $approvedIdentitiesToCreate: [Int]
    $approvedIdentitiesToRemove: [Int]
  ) {
    approveIndividualDataChange(
      grievanceTicketId: $grievanceTicketId
      individualApproveData: $individualApproveData
      flexFieldsApproveData: $flexFieldsApproveData
      approvedDocumentsToCreate: $approvedDocumentsToCreate
      approvedDocumentsToRemove: $approvedDocumentsToRemove
      approvedIdentitiesToCreate: $approvedIdentitiesToCreate
      approvedIdentitiesToRemove: $approvedIdentitiesToRemove
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
