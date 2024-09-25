import { gql } from '@apollo/client';

export const UPDATE_PROGRAM_MUTATION = gql`
  mutation UpdateProgram($programData: UpdateProgramInput!, $version: BigInt!) {
    updateProgram(programData: $programData, version: $version) {
      program {
        ...programDetails
      }
      validationErrors
    }
  }
`;
