import { gql } from '@apollo/client';

export const ExistingGrievanceTickets = gql`
  query ExistingGrievanceTickets(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $id: UUID
    $businessArea: String!
    $household: ID
    $individual: ID
    $paymentRecord: [ID]
    $category: String
    $issueType: String
    $orderBy: String
  ) {
    existingGrievanceTickets(
      before: $before
      after: $after
      first: $first
      last: $last
      id: $id
      businessArea: $businessArea
      household: $household
      individual: $individual
      paymentRecord: $paymentRecord
      category: $category
      issueType: $issueType
      orderBy: $orderBy
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
          unicefId
          status
          assignedTo {
            id
            firstName
            lastName
            email
          }
          category
          createdAt
          issueType
          userModified
          admin
          household {
            unicefId
            id
          }
          individual {
            unicefId
            id
          }
        }
      }
    }
  }
`;
