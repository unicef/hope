import { gql } from '@apollo/client';

export const DeleteTargetPopulation = gql`
  mutation DeleteTargetPopulation(
    $input: DeleteTargetPopulationMutationInput!
  ) {
    deleteTargetPopulation(input: $input) {
      clientMutationId
    }
  }
`;
