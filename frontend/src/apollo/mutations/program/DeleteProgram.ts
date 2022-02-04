import { gql } from 'apollo-boost';

export const DELETE_PROGRAM_MUTATION = gql`
  mutation DeleteProgram($programId: String!) {
    deleteProgram(programId: $programId) {
      ok
    }
  }
`;
