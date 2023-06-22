import { gql } from 'apollo-boost';

export const AvailableFlows = gql`
  query AvailableFlows {
    availableFlows {
      id
      name
    }
  }
`;
