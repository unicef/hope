import { gql } from '@apollo/client';

export const FinalizeTP = gql`
  mutation FinalizeTP($id: ID!) {
    finalizeTargetPopulation(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;
