import { gql } from 'apollo-boost';
export const ApproveTargetPopulation = gql`
  mutation ApproveTP($id: ID!) {
    approveTargetPopulation(id: $id) {
      targetPopulation {
        status
      }
    }
  }
`;
