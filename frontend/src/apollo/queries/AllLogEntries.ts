import { gql } from 'apollo-boost';

export const ALL_LOG_ENTRIES_QUERY = gql`
  query AllLogEntries(
    $objectId: String!
    $after: String
    $before: String
    $count: Int
  ) {
    allLogEntries(
      after: $after
      before: $before
      first: $count
      objectId: $objectId
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edges {
        cursor
        node {
          id
          action
          changesDisplayDict
          timestamp
          actor{
            id
            firstName
            lastName
          }
        }
      }
    }
  }
`;
