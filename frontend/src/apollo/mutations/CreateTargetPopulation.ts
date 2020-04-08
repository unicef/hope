import { gql } from 'apollo-boost';

export const CreateTargetPopulation = gql`
  mutation CreateTargetPopulation($input: CreateTargetPopulationMutationInput!) {
    createTargetPopulation(input: $input) {
      targetPopulation {
        id
        status
      }
    }
  }
`;
