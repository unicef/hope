import { gql } from '@apollo/client';

export const UnlockTargetPopulation = gql`
  mutation UnlockTP($id: ID!) {
    unlockTargetPopulation(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;
