import { gql } from 'apollo-boost';

export const RebuildTargetPopulation = gql`
  mutation RebuildTP($id: ID!) {
    targetPopulationRebuild(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;
