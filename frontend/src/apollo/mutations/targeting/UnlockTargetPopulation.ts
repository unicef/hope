import { gql } from 'apollo-boost';

export const UnlockTargetPopulation = gql`
  mutation UnlockTP($id: ID!) {
    unlockTargetPopulation(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;