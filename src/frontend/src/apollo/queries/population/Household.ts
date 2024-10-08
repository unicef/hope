import { gql } from '@apollo/client';

export const HOUSEHOLD_QUERY = gql`
  query Household($id: ID!) {
    household(id: $id) {
      ...householdDetailed
    }
  }
`;
