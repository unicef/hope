import { gql } from '@apollo/client';

export const CREATE_PROGRAM_MUTATION = gql`
  mutation CreateProgram($programData: CreateProgramInput!) {
    createProgram(programData: $programData) {
      program {
        id
      }
      validationErrors
    }
  }
`;
