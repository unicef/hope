import { gql } from '@apollo/client';

export const DuplicateTargetPopulation = gql`
  mutation CopyTargetPopulation($input: CopyTargetPopulationMutationInput!) {
    copyTargetPopulation(input: $input) {
      clientMutationId
      targetPopulation {
        id
      }
      validationErrors
    }
  }
`;
