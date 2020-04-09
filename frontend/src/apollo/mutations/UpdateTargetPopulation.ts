import { gql } from 'apollo-boost';

export const UpdateTP = gql`
  mutation UpdateTP($input: UpdateTargetPopulationInput!) {
    updateTargetPopulation(input: $input) {
      targetPopulation {
        id
        status
      }
    }
  }
`;
