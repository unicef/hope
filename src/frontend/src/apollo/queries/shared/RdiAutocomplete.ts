import { gql } from '@apollo/client';

export const RdiAutocomplete = gql`
  query RdiAutocomplete(
    $businessArea: String
    $first: Int
    $orderBy: String
    $name: String
  ) {
    allRegistrationDataImports(
      businessArea: $businessArea
      first: $first
      orderBy: $orderBy
      name_Startswith: $name
    ) {
      edges {
        cursor
        node {
          id
          name
        }
      }
    }
  }
`;
