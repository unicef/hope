import { gql } from '@apollo/client';

export const INDIVIDUAL_QUERY = gql`
  query Individual($id: ID!, $rdiMergeStatus: String) {
    individual(id: $id, rdiMergeStatus: $rdiMergeStatus) {
      ...individualDetailed
    }
  }
`;
