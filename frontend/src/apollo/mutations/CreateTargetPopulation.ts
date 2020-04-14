import { gql } from 'apollo-boost';

export const CreateTP = gql`
  mutation CreateTP($input: CreateTargetPopulationInput!) {
    createTargetPopulation(input: $input) {
      targetPopulation {
        id
        status
      }
    }
  }
`;
