import { gql } from 'apollo-boost';
export const ApproveTargetPopulation = gql`
  mutation ApproveTP($id: ID!, $programId: ID!) {
    approveTargetPopulation(id: $id, programId: $programId) {
      targetPopulation {
        status
      }
    }
  }
`;
