import { gql } from '@apollo/client';

export const RebuildTargetPopulation = gql`
  mutation RebuildTP($id: ID!) {
    targetPopulationRebuild(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;
