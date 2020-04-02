import { gql } from 'apollo-boost';

export const DuplicateTargetPopulation = gql`
  mutation CopyTargetPopulation($input: CopyTargetPopulationMutationInput!) {
    copyTargetPopulation(
      input: $input
    ) {
      clientMutationId
    }
  }
`;
