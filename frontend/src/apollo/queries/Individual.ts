import { gql } from 'apollo-boost';

export const INDIVIDUAL_QUERY = gql`
  query Individual($id: ID!) {
    individual(id: $id) {
      ...individualDetailed
    }
  }
`;
