import { gql } from 'apollo-boost';

export const AllTargetPopulations = gql`
  query AllTargetPopulations(
    $after: String
    $before: String
    $first: Int
    $last: Int
  ) {
    allTargetPopulation(
      after: $after
      before: $before
      first: $first
      last: $last
    ) {
      edges {
        node {
          id
          name
          status
          createdAt
          createdBy {
            firstName
            lastName
          }
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
