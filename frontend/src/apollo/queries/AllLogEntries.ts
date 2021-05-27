import {gql} from 'apollo-boost';

export const ALL_LOG_ENTRIES_QUERY = gql`
  query AllLogEntries(
    $businessArea: String!
    $objectId: UUID
    $after: String
    $before: String
    $first: Int
    $last: Int
    $search: String
    $module: String
  ) {
    allLogEntries(
      after: $after
      before: $before
      first: $first
      last: $last
      objectId: $objectId
      businessArea: $businessArea
      search: $search
      module: $module
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
          changes
          objectRepr
          objectId
          timestamp
          contentType{
            id
            appLabel
            model
            name
          }
          user {
            id
            firstName
            lastName
          }
        }
      }
    }
    logEntryActionChoices{
      name
      value
    }
  }
`;
