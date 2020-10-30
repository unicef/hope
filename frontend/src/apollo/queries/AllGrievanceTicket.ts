import { gql } from 'apollo-boost';

export const AllGrievanceTicket = gql`
  query AllGrievanceTicket(
    $before: String
    $after: String
    $businessArea: String!
    $first: Int
    $last: Int
    $orderBy: String
  ) {
    allGrievanceTicket(
      before: $before
      after: $after
      first: $first
      last: $last
      orderBy: $orderBy
      businessArea: $businessArea
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
          category
          assignedTo {
            id
            firstName
            lastName
          }
          createdAt
          userModified
        }
      }
    }
  }
`;
