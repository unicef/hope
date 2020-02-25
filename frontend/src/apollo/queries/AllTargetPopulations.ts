import { gql } from 'apollo-boost';

export const AllTargetPopulations = gql`
  query AllTargetPopulations($count: Int) {
    allTargetPopulation(first: $count) {
      edges {
        node {
          name
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
