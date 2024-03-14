import { gql } from '@apollo/client';

export const INDIVIDUAL_QUERY = gql`
  query Individual($id: ID!) {
    individual(id: $id) {
      ...individualDetailed
    }
  }
`;
