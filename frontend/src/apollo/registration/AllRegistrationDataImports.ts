import { gql } from 'apollo-boost';

export const ALL_REGISTRATION_DATA_IMPORT_QUERY = gql`
  query AllRegistrationDataImports(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $name_Icontains: String
    $importedBy_Id: UUID
    $status: String
    $importDate: Date
  ) {
    allRegistrationDataImports(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name_Icontains: $name_Icontains
      importedBy_Id: $importedBy_Id
      status: $status
      importDate: $importDate
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
            ...registrationFragmentMinimal
        }
      }
    }
  }
`;
