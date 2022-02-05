import { gql } from 'apollo-boost';

export const HOUSEHOLD_FLEX_FIELDS_QUERY = gql`
  query HouseholdFlexFields($id: ID!) {
    household(id: $id) {
      id
      flexFields
    }
  }
`;
