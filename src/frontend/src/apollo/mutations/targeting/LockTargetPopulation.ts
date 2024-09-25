import { gql } from '@apollo/client';

export const LockTargetPopulation = gql`
  mutation LockTP($id: ID!) {
    lockTargetPopulation(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;
