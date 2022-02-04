import { gql } from 'apollo-boost';

export const HOUSEHOLD_QUERY = gql`
  query Household($id: ID!) {
    household(id: $id) {
      ...householdDetailed
    }
  }
`;
