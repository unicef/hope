import { gql } from '@apollo/client';

export const CreateTP = gql`
  mutation CreateTP($input: CreateTargetPopulationInput!) {
    createTargetPopulation(input: $input) {
      targetPopulation {
        id
        status
        totalHouseholdsCount
        totalIndividualsCount
      }
      validationErrors
    }
  }
`;
