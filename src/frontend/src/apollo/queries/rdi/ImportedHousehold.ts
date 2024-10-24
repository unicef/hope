import { gql } from '@apollo/client';

export const IMPORTED_HOUSEHOLD_QUERY = gql`
  query ImportedHousehold($id: ID!) {
    importedHousehold(id: $id) {
      ...importedHouseholdDetailed
    }
  }
`;
