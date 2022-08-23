import { gql } from 'apollo-boost';

export const LockTargetPopulation = gql`
  mutation LockTP($id: ID!) {
    lockTargetPopulation(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;
