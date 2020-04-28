import { gql } from 'apollo-boost';

export const AllTargetPopulations = gql`
  query AllTargetPopulations(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $name: String
    $status: String
    $candidateListTotalHouseholdsMin: Int
    $candidateListTotalHouseholdsMax: Int
  ) {
    allTargetPopulation(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name: $name
      status: $status
      candidateListTotalHouseholdsMin: $candidateListTotalHouseholdsMin
      candidateListTotalHouseholdsMax: $candidateListTotalHouseholdsMax
    ) {
      edges {
        node {
          id
          name
          status
          createdAt
          updatedAt
          candidateListTotalHouseholds
          finalListTotalHouseholds
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
