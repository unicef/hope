import { gql } from '@apollo/client';

export const PROGRAM_QUERY = gql`
  query Program($id: ID!) {
    program(id: $id) {
      ...programDetails
    }
  }
`;
