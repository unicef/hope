import { gql } from '@apollo/client';

export const ApproveIndividualDataChange = gql`
  mutation ApproveIndividualDataChange(
    $grievanceTicketId: ID!
    $individualApproveData: JSONString
    $flexFieldsApproveData: JSONString
    $approvedDocumentsToCreate: [Int]
    $approvedDocumentsToRemove: [Int]
    $approvedDocumentsToEdit: [Int]
    $approvedIdentitiesToCreate: [Int]
    $approvedIdentitiesToEdit: [Int]
    $approvedIdentitiesToRemove: [Int]
    $approvedAccountsToCreate: [Int]
    $approvedAccountsToEdit: [Int]
  ) {
    approveIndividualDataChange(
      grievanceTicketId: $grievanceTicketId
      individualApproveData: $individualApproveData
      flexFieldsApproveData: $flexFieldsApproveData
      approvedDocumentsToCreate: $approvedDocumentsToCreate
      approvedDocumentsToRemove: $approvedDocumentsToRemove
      approvedDocumentsToEdit: $approvedDocumentsToEdit
      approvedIdentitiesToCreate: $approvedIdentitiesToCreate
      approvedIdentitiesToEdit: $approvedIdentitiesToEdit
      approvedIdentitiesToRemove: $approvedIdentitiesToRemove
      approvedAccountsToCreate: $approvedAccountsToCreate
      approvedAccountsToEdit: $approvedAccountsToEdit
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
