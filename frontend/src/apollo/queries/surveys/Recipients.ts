import { gql } from 'apollo-boost';

export const Recipients = gql`
  query Recipients(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $survey: String!
    $orderBy: String
  ) {
    recipients(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      survey: $survey
      orderBy: $orderBy
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edgeCount
      edges {
        cursor
        node {
          id
          headOfHousehold {
            id
            fullName
            household {
              id
              unicefId
              size
              status
              admin2 {
                id
                name
              }
              residenceStatus
              lastRegistrationDate
            }
          }
        }
      }
    }
  }
`;
