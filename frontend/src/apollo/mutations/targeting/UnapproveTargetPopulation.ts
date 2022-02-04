import { gql } from 'apollo-boost';
export const UnapproveTargetPopulation = gql`
  mutation UnapproveTP($id: ID!) {
    unapproveTargetPopulation(id: $id) {
      targetPopulation {
        ...targetPopulationDetailed
      }
    }
  }
`;