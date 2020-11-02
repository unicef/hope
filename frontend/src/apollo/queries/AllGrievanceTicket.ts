import { gql } from 'apollo-boost';

export const AllGrievanceTicket = gql`
  query AllGrievanceTicket(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $id: UUID
    $category: String
    $businessArea: String!
    $search: String
    $status: [String]
    $fsp: [ID]
    $createdAtRange: String
    $orderBy: String
  ) {
    allGrievanceTicket(
      before: $before
      after: $after
      first: $first
      last: $last
      id: $id
      category: $category
      businessArea: $businessArea
      search: $search
      status: $status
      fsp: $fsp
      createdAtRange: $createdAtRange
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
          }
          category
          createdAt
          userModified
        }
      }
    }
  }
`;
