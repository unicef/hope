import { gql } from '@apollo/client';

export const UpdateTP = gql`
  mutation UpdateTP($input: UpdateTargetPopulationInput!) {
    updateTargetPopulation(input: $input) {
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
