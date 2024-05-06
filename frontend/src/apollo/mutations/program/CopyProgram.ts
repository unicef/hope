import { gql } from '@apollo/client';

export const COPY_PROGRAM_MUTATION = gql`
  mutation CopyProgram($programData: CopyProgramInput!) {
    copyProgram(programData: $programData) {
      program {
        id
      }
      validationErrors
    }
  }
`;
