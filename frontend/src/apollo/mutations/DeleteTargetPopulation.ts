import { gql } from 'apollo-boost';

export const DeleteTargetPopulation = gql`
  mutation DeleteTargetPopulation($input: DeleteTargetPopulationMutationInput!) {
    deleteTargetPopulation(input: $input) {
      clientMutationId
    }
  }
`;
