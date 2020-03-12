import { gql } from 'apollo-boost';

export const IMPORTED_HOUSEHOLD_QUERY = gql`
  query AllImportedHouseholds($id: ID!) {
    importedHousehold(id: $id) {
      ...importedHouseholdMinimal
    }
  }
`;
