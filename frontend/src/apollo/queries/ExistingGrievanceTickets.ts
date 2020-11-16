import { gql } from 'apollo-boost';

export const ExistingGrievanceTickets = gql`
  query ExistingGrievanceTickets(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $id: UUID
    $businessArea: String!
    $category: String!
    $issueType: String
    $household: ID
    $individual: ID
    $paymentRecord: [ID]
    $orderBy: String
  ) {
    existingGrievanceTickets(
      before: $before
      after: $after
      first: $first
      last: $last
      id: $id
      businessArea: $businessArea
      category: $category
      issueType: $issueType
      household: $household
      individual: $individual
      paymentRecord: $paymentRecord
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
          status
          assignedTo {
            id
            firstName
            lastName
            email
          }
          category
          createdAt
          userModified
          admin
          household {
            unicefId
            id
          }
        }
      }
    }
  }
`;
