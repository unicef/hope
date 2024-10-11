import { gql } from '@apollo/client';

export const AllGrievanceTicket = gql`
  query AllGrievanceTicket(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $id: UUID
    $category: String
    $issueType: String
    $businessArea: String!
    $search: String
    $documentType: String
    $documentNumber: String
    $status: [String]
    $fsp: String
    $createdAtRange: String
    $admin1: ID
    $admin2: ID
    $orderBy: String
    $registrationDataImport: ID
    $assignedTo: ID
    $createdBy: ID
    $cashPlan: String
    $scoreMin: String
    $scoreMax: String
    $household: String
    $grievanceType: String
    $grievanceStatus: String
    $priority: String
    $urgency: String
    $preferredLanguage: String
    $program: String
    $isActiveProgram: Boolean
    $isCrossArea: Boolean
  ) {
    allGrievanceTicket(
      before: $before
      after: $after
      first: $first
      last: $last
      id: $id
      category: $category
      issueType: $issueType
      businessArea: $businessArea
      search: $search
      documentType: $documentType
      documentNumber: $documentNumber
      status: $status
      fsp: $fsp
      createdAtRange: $createdAtRange
      orderBy: $orderBy
      admin1: $admin1
      admin2: $admin2
      registrationDataImport: $registrationDataImport
      assignedTo: $assignedTo
      createdBy: $createdBy
      cashPlan: $cashPlan
      scoreMin: $scoreMin
      scoreMax: $scoreMax
      household: $household
      grievanceType: $grievanceType
      grievanceStatus: $grievanceStatus
      priority: $priority
      urgency: $urgency
      preferredLanguage: $preferredLanguage
      program: $program
      isActiveProgram: $isActiveProgram
      isCrossArea: $isCrossArea
    ) {
      totalCount
      pageInfo {
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          id
          status
          assignedTo {
            id
            firstName
            lastName
            email
          }
          createdBy {
            id
          }
          category
          issueType
          createdAt
          userModified
          admin
          household {
            unicefId
            id
          }
          unicefId
          relatedTickets {
            id
          }
          priority
          urgency
          updatedAt
          totalDays
          programs {
            id
            name
          }
        }
      }
    }
  }
`;
