import { gql } from 'apollo-boost';

export const FinalizeTP = gql`
  mutation FinalizeTP($id: ID!) {
    finalizeTargetPopulation(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;
