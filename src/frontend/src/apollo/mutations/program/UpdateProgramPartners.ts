import { gql } from '@apollo/client';

export const UPDATE_PROGRAM_PARTNERS_MUTATION = gql`
  mutation UpdateProgramPartners(
    $programData: UpdateProgramPartnersInput
    $version: BigInt
  ) {
    updateProgramPartners(programData: $programData, version: $version) {
      program {
        ...programDetails
      }
    }
  }
`;
