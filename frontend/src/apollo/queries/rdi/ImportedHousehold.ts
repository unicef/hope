import { gql } from 'apollo-boost';

export const IMPORTED_HOUSEHOLD_QUERY = gql`
  query ImportedHousehold($id: ID!) {
    importedHousehold(id: $id) {
      ...importedHouseholdDetailed
    }
  }
`;
