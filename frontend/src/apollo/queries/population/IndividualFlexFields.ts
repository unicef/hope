import { gql } from 'apollo-boost';

export const INDIVIDUAL_FLEX_FIELDS_QUERY = gql`
  query IndividualFlexFields($id: ID!) {
    individual(id: $id) {
      id
      flexFields
    }
  }
`;
