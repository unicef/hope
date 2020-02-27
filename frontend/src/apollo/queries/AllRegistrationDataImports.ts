import { gql } from 'apollo-boost';

export const ALL_REGISTRATION_DATA_IMPORT_QUERY = gql`
  query AllRegistrationDataImports(
    $after: String
    $before: String
    $first: Int
    $last: Int
  ) {
    allRegistrationDataImports(
      after: $after
      before: $before
      first: $first
      last: $last
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
          createdAt
          name
          status
          importDate
          importedBy {
            id
            firstName
            lastName
          }
          dataSource
          numberOfHouseholds
          numberOfHouseholds
        }
      }
    }
  }
`;
