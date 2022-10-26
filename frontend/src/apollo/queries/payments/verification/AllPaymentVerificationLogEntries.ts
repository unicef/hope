import { gql } from 'apollo-boost';

export const ALL_PAYMENT_VERIFICATION_LOG_ENTRIES_QUERY = gql`
  query AllPaymentVerificationLogEntries(
    $businessArea: String!
    $objectId: UUID
    $objectType: String
    $after: String
    $before: String
    $first: Int
    $last: Int
    $search: String
    $module: String
  ) {
    allPaymentVerificationLogEntries(
      after: $after
      before: $before
      first: $first
      last: $last
      objectId: $objectId
      objectType: $objectType
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
          contentType {
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
          contentObject {
            id
            unicefId
          }
        }
      }
    }
    logEntryActionChoices {
      name
      value
    }
  }
`;
